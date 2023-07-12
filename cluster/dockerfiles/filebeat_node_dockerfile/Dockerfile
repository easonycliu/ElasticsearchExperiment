FROM docker.elastic.co/beats/filebeat:8.7.1
USER root
RUN groupadd docker && usermod -aG docker filebeat && groupmod -g 998 docker
USER filebeat
RUN sed -i "7s/false/true/" /usr/share/filebeat/modules.d/elasticsearch.yml.disabled
CMD ["/bin/bash", "-c", "/usr/share/filebeat/filebeat modules enable elasticsearch && /usr/share/filebeat/filebeat setup && /usr/share/filebeat/filebeat -e"]