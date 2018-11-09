FROM ubuntu:18.10
 
# Update OS and create superuser
RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install python3-dev python3-pip
# RUN apt-get -y install python-minimal python-pip
# RUN pip2 install supervisor supervisor-stdout 

# Install Python
COPY reqs.txt .
RUN pip3 install -r reqs.txt

# Expose port for connection
EXPOSE 5000

# Add requirements.txt
RUN mkdir /app
ENV HOME /app
WORKDIR /app

# ADD conf/supervisor.conf /etc/supervisor.conf
# ADD conf/nginx.conf /etc/nginx/nginx.conf

# # Server configuration
# COPY conf .
# RUN sudo supervisorctl reread && \
#     sudo service supervisor restart && \
#     sudo supervisorctl status

# Run uwsgi server during startup from configuration file
# ENTRYPOINT ["supervisord", "-c", "/etc/supervisor.conf", "-n"]
# ENTRYPOINT [ "python3", "main.py"]
# ENTRYPOINT ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "main:app"]
ENTRYPOINT [ "app.py"]