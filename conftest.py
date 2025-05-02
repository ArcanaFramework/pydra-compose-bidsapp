import os
import pytest
import typing as ty
from tempfile import mkdtemp
from pathlib import Path
from fileformats.medimage import NiftiGzX

PKG_DIR = Path(__file__).parent


@pytest.fixture
def work_dir() -> Path:  # type: ignore[misc]
    # work_dir = Path.home() / '.frametree-tests'
    # work_dir.mkdir(exist_ok=True)
    # return work_dir
    work_dir = mkdtemp()
    yield Path(work_dir)
    # shutil.rmtree(work_dir)


@pytest.fixture(scope="session")
def pkg_dir() -> Path:
    return PKG_DIR


@pytest.fixture(scope="session")
def nifti_sample_dir(pkg_dir):
    return pkg_dir / "test-data" / "nifti"


# FIXME: should be converted to python script to be Windows compatible
@pytest.fixture(scope="session")
def mock_bids_app_script():
    file_tests = ""
    for inpt_path, datatype in [
        ("anat/T1w", NiftiGzX),
        ("anat/T2w", NiftiGzX),
        ("dwi/dwi", NiftiGzX),
    ]:
        subdir, suffix = inpt_path.split("/")
        fpath = (
            f"$BIDS_DATASET/sub-${{SUBJ_ID}}/{subdir}/"
            f"sub-${{SUBJ_ID}}_{suffix}{datatype.ext}"
        )
        file_tests += f"""
        if [ ! -f {fpath} ]; then
            echo "Did not find {suffix} file at {fpath}"
            exit 1;
        fi
        """

    return f"""#!/bin/sh
BIDS_DATASET=$1
OUTPUTS_DIR=$2
SUBJ_ID=$5
{file_tests}
# Write mock output files to 'derivatives' Directory
mkdir -p $OUTPUTS_DIR
echo 'file1' > $OUTPUTS_DIR/sub-${{SUBJ_ID}}_file1.txt
echo 'file2' > $OUTPUTS_DIR/sub-${{SUBJ_ID}}_file2.txt
"""


# For debugging in IDE's don't catch raised exceptions and let the IDE
# break at it
if os.getenv("_PYTEST_RAISE", "0") != "0":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call: pytest.CallInfo[ty.Any]) -> None:
        if call.excinfo is not None:
            raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo: pytest.ExceptionInfo[BaseException]) -> None:
        raise excinfo.value

    CATCH_CLI_EXCEPTIONS = False
else:
    CATCH_CLI_EXCEPTIONS = True
