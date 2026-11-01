"""Storage layout and naming conventions for Tesouro Direto files.

Files are stored under ``<dataset_id>/`` directly (Padrão B). Filenames embed
the upstream ``last_modified`` timestamp using the pattern
``<slug>@<YYYYMMDDTHHMMSS>.csv`` so multiple snapshots of the same resource
coexist.
"""

import datetime as dt
from pathlib import Path

from quantilica.core.storage import StampedDataRepository, slugify, stamp_filename


class DataRepository(StampedDataRepository):
    """Tesouro Direto data store using the ``<dataset_id>/`` layout."""

    def list_datasets(self) -> list[str]:
        """Alias for ``list_dataset_ids`` to match CLI usage.

        Returns:
            list[str]: A list of dataset IDs available in the repository.
        """
        return self.list_dataset_ids()

    def get_all_latest_files(self, dataset_id: str) -> list[Path]:
        """Alias for ``get_all_latest_stamped_files`` to match CLI usage.

        Args:
            dataset_id (str): The ID of the dataset to retrieve files for.

        Returns:
            list[Path]: A list of paths to the latest files for the given dataset.
        """
        return self.get_all_latest_stamped_files(dataset_id)

    def file_path(self, dataset_id: str, filename: str) -> Path:
        """Return the absolute path of ``filename`` under ``dataset_id``.

        Args:
            dataset_id (str): The ID of the dataset.
            filename (str): The name of the file.

        Returns:
            Path: The absolute path to the file.
        """
        return self.dataset_path(dataset_id, filename)

    def path_for_entry(
        self, entry: dict, last_modified: dt.date | dt.datetime | None = None
    ) -> Path:
        """Calculate the destination path for a given entry.

        Args:
            entry (dict): The dataset entry metadata.
            last_modified (dt.date | dt.datetime | None, optional): The last modified
                timestamp. Defaults to None.

        Returns:
            Path: The destination path for the entry.
        """
        ckan_res = entry.get("ckan_resource") or {}
        ckan_str = ckan_res.get("last_modified") or ckan_res.get("created")

        last_mod_str: str | None = None
        if isinstance(last_modified, dt.datetime):
            last_mod_str = last_modified.isoformat()
        elif isinstance(last_modified, dt.date):
            ckan_dt: dt.datetime | None = None
            if ckan_str:
                try:
                    ckan_dt = dt.datetime.fromisoformat(ckan_str)
                except ValueError:
                    ckan_dt = None
            if ckan_dt and ckan_dt.date() == last_modified:
                last_mod_str = ckan_str
            else:
                last_mod_str = last_modified.isoformat()
        elif ckan_str:
            last_mod_str = ckan_str

        filename = self.generate_filename(entry["id"], last_mod_str)
        return self.dataset_path(entry["group"], filename)

    @staticmethod
    def generate_filename(name: str, last_modified: str | None = None) -> str:
        """Return ``<slug>@<YYYYMMDDTHHMMSS>.csv`` for a CKAN resource.

        Returns ``<slug>.csv`` (no stamp) when ``last_modified`` is absent or
        unparseable, rather than inventing a timestamp.

        Args:
            name (str): The base name of the resource.
            last_modified (str | None, optional): ISO formatted last modified string.
                Defaults to None.

        Returns:
            str: The generated filename.
        """
        name_slug = slugify(name)
        timestamp: dt.datetime | None = None
        if last_modified:
            try:
                timestamp = dt.datetime.fromisoformat(last_modified)
            except ValueError:
                pass
        return stamp_filename(name_slug, "csv", timestamp, precision="datetime")
