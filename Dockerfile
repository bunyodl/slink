FROM python:3.14-alpine

# create group and user
RUN addgroup -S slink_group && \
    adduser -S bunyod -G slink_group

WORKDIR /app

COPY requirements.txt ./

# install dependencies as root
RUN pip install --no-cache-dir -r requirements.txt

# copy source code
COPY . .

# change ownership
RUN chown -R bunyod:slink_group /app

# switch to non-root user
USER bunyod

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]