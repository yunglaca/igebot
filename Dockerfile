FROM python:3.12-slim as app
ENV PYTHONPATH "${PYTHONPATH}:/igebot/app"
WORKDIR /igebot
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "./start.sh" ]