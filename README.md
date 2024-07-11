# Citation Location Extract

## Introduction
This project hopes to extract the citation location(or citation context, means the paragraph citation locates) from papers which refers target article. If you have any question, please create an issue so that we can make it better.

At first you should prepare tei-format full papers, or deploy a grobid server to transfer pdf to tei-format xml. For each target paper you need a json file to show citing papers' tei-format file paths. Such as:
```json
{
    "paper_title": "tei-xml file path",
    "paper_title2": "tei-xml file path2",
     ...
}
```
Please make sure your JSON format is correct.

## Deploy

### Python env
The programming language we use is python, and you may need to setup python env if you want to exec or fix this project, you can read `docs/env_extract.md`.

### Grobid Service

We use grobid service to transfer pdf to tei-format xml, if you want to deploy the Grobid service. Please follow the instructions by visiting the link: https://grobid.readthedocs.io/en/latest.

And if you want to use your own request method, you can refer to the link below: https://grobid.readthedocs.io/en/latest/Grobid-service/#grobid-web-services
