import logging
import urllib

import requests
import typer
from bs4 import BeautifulSoup
from pydantic import HttpUrl
from requests.adapters import HTTPAdapter
from typer import Typer
from urllib3 import Retry

from src.utils import clean_extracted_text, valid_pydantic_type

cli = Typer(no_args_is_help=True)


@cli.command(name="get")
def get_content_url(
        url: str = typer.Option(..., help="URL of the article to extract the content."),
        limit_clean: int = typer.Option(100, help="Number of try to clean the text extracted."),
) -> str:
    """
    Get the content of an article from a URL.

    Args:
        url (str): URL of the article to extract the content.
        limit_clean (int): Number of try to clean the text extracted
    """
    # Validation of input parameters
    valid_pydantic_type(url, HttpUrl)

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "fr-FR,fr;q=0.9",
        "cache-control": "max-age=0",
        "cookie": (
            "ak-inject-mpulse=false; _tms_journey=%7B%22evt%22%3A%7B%22push_subscription%22%3A0%2C%22pwa_popin%22%3A0%2C%22app_banner%22%3A0%7D%2C%22pagesRead%22%3A1%2C%22end%22%3A%22Mon%2C%2005%20Aug%202024%2011%3A02%3A33%20GMT%22%7D; _tms_ab_popinSurvey=22; "
            "euconsent-v2=CQChJMAQChJMAAHABBENA-FsAP_gAAAAAAqIJvFF_G7eTSFhcWp3YftEOY0ewVA74sAhBgCJA4gBCBpAsJQEkGAAIADAIAAKAAIAIGZBAAFlAADABEAAYIABICDMAAAAIRAAICAAAAABAgBACABIEwAAAAIAgEBUABUAiQIAABogwMBAAAAgBEAAAAIgAIABAAAAACAAQAAQAAAIAggAAAAAAAAAAAAEABAAEAAAAAECAAAAAAAcABAAAAMSgAwABBS4pABgACClw6ADAAEFLiEAGAAIKXBIAMAAQUuLQAYAAgpc.f_wAAAAAAAAA; "
            "_pprv=eyJjb25zZW50Ijp7IjAiOnsibW9kZSI6Im9wdC1pbiJ9LCIxIjp7Im1vZGUiOiJvcHQtaW4ifSwiMiI6eyJtb2RlIjoib3B0LWluIn0sIjMiOnsibW9kZSI6Im9wdC1pbiJ9LCI0Ijp7Im1vZGUiOiJvcHQtaW4ifSwiNSI6eyJtb2RlIjoib3B0LWluIn0sIjYiOnsibW9kZSI6Im9wdC1pbiJ9LCI3Ijp7Im1vZGUiOiJvcHQtaW4ifX0sInB1cnBvc2VzIjpudWxsLCJfdCI6Im1ldmFvaHQwfGx6NnZyMGgwIn0%3D; "
            "_tms_ab_hotjar=54; _pcid=%7B%22browserId%22%3A%22lz6vr0gvtvxjllz6%22%2C%22_t%22%3A%22mevaojir%7Clz6vr26r%22%7D; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXSwH18yBbKADdClAFb0wAH1QAvAGxCYAJnlgQAXyA; _fbp=fb.1.1722250955728.872917922494461594; "
            "ownpage_fp2=82e4bd92fe280bde; __qca=P0-525654283-1722250955647; nli=3dc2a11c-9dbb-5cb3-1471-c506e2bb7c04; _tfpvi=M2U2ZmFmYTQtYWY4Ni00YmIzLWJhZWMtMGQ5ZjU5ZjE5MzcyIzUtNg%3D%3D; dicbo_id=%7B%22dicbo_fetch%22%3A1722250955994%7D; "
            "__gads=ID=083877495f23fdfd:T=1722250957:RT=1722250957:S=ALNI_MZcd3WV2qvZsxWuUwB1JT9_YXdomg; __gpi=UID=00000ea7977e2f6c:T=1722250957:RT=1722250957:S=ALNI_Ma8ND-Fxs27ZDJkQa5UrLmiZGzzgw; __eoi=ID=d2deefc773f751da:T=1722250957:RT=1722250957:S=AA-AfjYodid2AAhg69KWDdB2ogFT; "
            "_cb=DB0aSBDuQOt5_tJ3K; _chartbeat2=.1722250956605.1722250956605.1.uu8i0Bj5luGh00OxDkafiZCrOTdF.1; _cb_svref=external; ivbsdid=%7B%22id%22%3A%22sn57r482179sln_94%22%7D; ivBlk=n"),
        "dpr": "1.25",
        "ect": "4g",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "viewport-width": "983"
    }

    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    response = http.get(url, headers=headers, allow_redirects=True, timeout=10)
    response.raise_for_status()

    # Check if the request is successful
    if response.status_code == 200:
        # Parser le contenu HTML de la page
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract the text from the <p> tags
        article_text = ""
        for paragraph in soup.find_all("p"):
            article_text += paragraph.get_text() + " "

        # article_text = soup.text

        # Clean the text extracted
        article_text = clean_extracted_text(article_text, limit_clean)

        # Return to console the content of the article (python src ... > file.txt)
        typer.echo(article_text)

        return article_text
    else:
        logging.error(f"Failing to fetch the content of the article. ({response.status_code=})")
        raise typer.Exit(1)
