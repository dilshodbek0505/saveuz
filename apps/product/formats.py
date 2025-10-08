import os
import uuid
from io import BytesIO
from pathlib import Path

from django.conf import settings

from import_export.formats.base_formats import XLSX
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import column_index_from_string, get_column_letter
from PIL import Image as PILImage, UnidentifiedImageError
from tablib import Dataset


class ImageAwareXLSX(XLSX):
    title = "xlsx (images)"

    image_column_name = "image"
    export_row_height = 192  # points (~256px)
    export_column_width = 40  # approx characters to fit ~256px
    export_image_max_size = (256, 256)  # pixels
    export_native_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}
    import_allowed_formats = {"jpeg", "jpg", "png"}

    def export_data(self, dataset, **kwargs):
        content = super().export_data(dataset, **kwargs)

        if not dataset.headers or self.image_column_name not in dataset.headers:
            return content

        image_col_idx = dataset.headers.index(self.image_column_name) + 1
        workbook = load_workbook(filename=BytesIO(content))
        sheet = workbook.active

        for row_number, row in enumerate(dataset.dict, start=2):
            image_value = row.get(self.image_column_name)
            if not image_value:
                continue

            file_path = image_value
            if not os.path.isabs(file_path):
                file_path = os.path.join(settings.MEDIA_ROOT, image_value)

            if not os.path.isfile(file_path):
                continue

            excel_image = self._prepare_excel_image(file_path)
            if excel_image is None:
                continue

            cell = sheet.cell(row=row_number, column=image_col_idx).coordinate
            excel_image.anchor = cell
            sheet.add_image(excel_image)

            sheet.cell(row=row_number, column=image_col_idx, value="")
            sheet.row_dimensions[row_number].height = max(
                sheet.row_dimensions[row_number].height or 0,
                self.export_row_height,
            )
            col_letter = get_column_letter(image_col_idx)
            sheet.column_dimensions[col_letter].width = max(
                sheet.column_dimensions[col_letter].width or 0,
                self.export_column_width,
            )

        output = BytesIO()
        workbook.save(output)
        return output.getvalue()

    def create_dataset(self, in_stream, **kwargs):
        if hasattr(in_stream, "read"):
            raw = in_stream.read()
        else:
            raw = in_stream

        if raw is None:
            raise TypeError("No data provided for import")

        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        elif isinstance(raw, memoryview):
            raw = raw.tobytes()
        elif isinstance(raw, bytearray):
            raw = bytes(raw)
        dataset = super().create_dataset(BytesIO(raw), **kwargs)

        if not isinstance(dataset, Dataset) or not dataset.headers:
            return dataset

        if self.image_column_name not in dataset.headers:
            return dataset

        image_col_idx = dataset.headers.index(self.image_column_name) + 1
        workbook = load_workbook(filename=BytesIO(raw))
        sheet = workbook.active

        media_root = Path(settings.MEDIA_ROOT)
        cache_dir = media_root / "import_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        for picture in getattr(sheet, "_images", []):
            anchor = getattr(picture, "anchor", None)
            if anchor is None:
                continue

            row_number = None
            column_number = None

            if hasattr(anchor, "_from"):
                row_number = anchor._from.row + 1
                column_number = anchor._from.col + 1
            elif isinstance(anchor, str):
                from openpyxl.utils.cell import coordinate_from_string

                column_letter, row_number = coordinate_from_string(anchor)
                column_number = column_index_from_string(column_letter)

            if row_number is None or column_number is None:
                continue

            if column_number != image_col_idx:
                continue

            dataset_row_index = row_number - 2  # compensate header
            if not (0 <= dataset_row_index < len(dataset)):
                continue

            image_bytes = picture._data()
            converted_path = self._save_import_image(image_bytes, cache_dir)
            if converted_path is None:
                continue

            relative_path = Path("import_cache") / converted_path.name

            dataset[dataset_row_index, image_col_idx - 1] = str(relative_path)

        return dataset

    def _prepare_excel_image(self, file_path):
        extension = Path(file_path).suffix.lower()
        try:
            with PILImage.open(file_path) as img:
                img = img.copy()
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA") if img.mode in ("P", "LA") else img.convert("RGB")

                if img.size != self.export_image_max_size:
                    img = img.resize(self.export_image_max_size, PILImage.LANCZOS)

                converted = BytesIO()
                img.save(converted, format="PNG")
                converted.seek(0)

            image = XLImage(converted)
            image.format = "png"
            return image
        except (UnidentifiedImageError, FileNotFoundError, OSError):
            return None

    def _save_import_image(self, image_bytes, cache_dir: Path):
        stream = BytesIO(image_bytes)
        try:
            with PILImage.open(stream) as image:
                original_format = (image.format or "PNG").lower()
                if original_format not in self.import_allowed_formats:
                    image = image.convert("RGBA")
                elif original_format in {"jpeg", "jpg"} and image.mode not in ("RGB", "L"):
                    image = image.convert("RGB")
                elif original_format == "png" and image.mode in ("P", "LA"):
                    image = image.convert("RGBA")

                if image.size != self.export_image_max_size:
                    image = image.resize(self.export_image_max_size, PILImage.LANCZOS)

                extension = "jpg" if original_format in {"jpeg", "jpg"} else "png"

                filename = f"{uuid.uuid4().hex}.{extension}"
                output_path = cache_dir / filename
                image.save(output_path, format=save_format)
                return output_path
        except (UnidentifiedImageError, OSError):
            return None
