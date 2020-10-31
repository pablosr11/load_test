FROM node:14 as build-stage
WORKDIR /app
COPY ./nginx.conf /nginx.conf
COPY package*.json /app/
RUN yarn install
COPY ./ /app/
RUN yarn build

FROM nginx:1.18
COPY --from=build-stage /app/build/ /usr/share/nginx/html
COPY --from=build-stage /nginx.conf /etc/nginx/conf.d/default.conf