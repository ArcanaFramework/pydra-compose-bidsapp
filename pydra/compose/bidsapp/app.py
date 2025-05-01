from pathlib import Path
from fileformats.generic import Directory
from pydra.compose import shell


@shell.define
class BidsApp(shell.Task["BidsApp.Outputs"]):

    dataset_path: Directory = shell.arg(
        help="Path to BIDS dataset in the container",
        position=1,
        argstr="'{dataset_path}'",
    )

    output_path: Path = shell.arg(
        help="Directory where outputs will be written in the container",
        position=2,
        argstr="'{output_path}'",
    )

    analysis_level: str = shell.arg(
        help="The analysis level the app will be run at",
        position=3,
        argstr="",
    )

    participant_label: str = shell.arg(
        help="The IDs to include in the analysis",
        argstr="--participant-label ",
        position=4,
    )

    flags: str = shell.arg(
        help="Additional flags to pass to the app",
        argstr="",
        position=-1,
    )

    work_dir: Path = shell.arg(
        help="Directory where the nipype temporary working directories will be stored",
        argstr="--work-dir '{work_dir}'",
    )

    setup_completed: bool = shell.arg(
        help="Dummy field to ensure that the BIDS dataset construction completes first"
    )

    class Outputs:

        completed: bool = shell.arg(
            help="a simple flag to indicate app has completed",
            callable=lambda: True,
        )
