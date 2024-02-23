FROM python:3.12-slim

WORKDIR /terraform-module-registry-github

COPY * /terraform-module-registry-github

RUN pip install -r requirements.txt

EXPOSE 443

ENTRYPOINT ["/terraform-module-registry-github/terraform-module-registry-github.py"]
