FROM node:20-slim

WORKDIR /app

COPY package.json ./
RUN npm install --production

RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip fonts-dejavu-core && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir reportlab

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["node", "server.js"]
