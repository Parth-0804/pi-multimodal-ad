from pathlib import Path
from collections import Counter
import zipfile

archives = [
    Path(
        "/home/student/Master_Thesis_WS/pi-multimodal-ad/"
        "gtc-data-experiment/low-frequency (CIs + Oil + Environment)/"
        "Exp-A_HDF5_LF.zip"
    ),
    Path(
        "/home/student/Master_Thesis_WS/pi-multimodal-ad/"
        "gtc-data-experiment/low-frequency (CIs)/"
        "Exp-A_HDF5_CI.zip"
    ),
]

for archive in archives:

    print("\n" + "=" * 90)
    print(archive)
    print("=" * 90)

    with zipfile.ZipFile(archive) as zf:

        members = [
            x for x in zf.infolist()
            if not x.is_dir()
        ]

        print(f"\nTotal files: {len(members)}")

        suffixes = Counter(
            Path(x.filename).suffix.lower()
            or "<no extension>"
            for x in members
        )

        print("\nFile types:")
        for suffix, count in suffixes.most_common():
            print(f"  {suffix:<15} {count}")

        print("\nFirst 50 files:")

        for member in members[:50]:
            print(
                f"{member.file_size / 1024**2:8.2f} MB   "
                f"{member.filename}"
            )

def inspect_nested_archive(
    outer_zip_path: Path,
) -> dict:
    """
    Inspect nested PHM ZIP structure:

        outer.zip
            -> Run-X.zip
                -> HDF5
                    -> HDF5 datasets
    """

    report = {
        "outer_zip": str(
            outer_zip_path
        ),
        "runs": {},
    }

    if not outer_zip_path.exists():

        report["error"] = (
            "Outer ZIP does not exist."
        )

        return report

    with zipfile.ZipFile(
        outer_zip_path,
        mode="r",
    ) as outer_zip:

        inner_archives = sorted(
            [
                name
                for name in outer_zip.namelist()
                if name.lower().endswith(
                    ".zip"
                )
            ],
            key=natural_key,
        )

        for inner_name in inner_archives:

            run = parse_run(
                inner_name
            )

            inner_bytes = outer_zip.read(
                inner_name
            )

            with zipfile.ZipFile(
                io.BytesIO(inner_bytes),
                mode="r",
            ) as inner_zip:

                h5_members = find_h5_members(
                    inner_zip
                )

                run_info = {
                    "inner_zip":
                        inner_name,

                    "run":
                        run,

                    "hdf5_count":
                        len(h5_members),

                    "hdf5_files":
                        h5_members,
                }

                # Inspect first HDF5
                if h5_members:

                    with tempfile.TemporaryDirectory() as td:

                        temp_dir = Path(td)

                        p = extract_zip_member_to_temp(
                            inner_zip,
                            h5_members[0],
                            temp_dir,
                        )

                        try:

                            run_info[
                                "first_hdf5"
                            ] = inspect_h5_file(
                                p
                            )

                        finally:

                            p.unlink(
                                missing_ok=True
                            )

                report["runs"][
                    f"Run-{run}"
                ] = run_info

    return report