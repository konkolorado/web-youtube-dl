import anyio
from rich.progress import Progress
from typer import Typer

from web_youtube_dl.client import DownloadClient
from web_youtube_dl.config import get_download_path

app = Typer()


async def _start_and_wait_for_download(url: str, wait_for: bool):
    async with DownloadClient() as client:
        response = await client.start_download(url)
        request_id = response["id"]

        if not wait_for:
            print(f"Started download for {request_id}")
            return

        with Progress(transient=True) as progress:
            dl = progress.add_task("[red]Downloading...", total=100)

            while not progress.finished:
                r = await client.get_download_status(request_id)
                progress.update(dl, completed=r["progress"])
                await anyio.sleep(0.5)

        print(f"Saved file to {get_download_path()}")


@app.command()
def start_download(url: str, wait_for: bool = True):
    anyio.run(_start_and_wait_for_download, url, wait_for)


if __name__ == "__main__":
    app()
