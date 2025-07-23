FROM registry.access.redhat.com/ubi9/python-311:1-66
WORKDIR /opt/app-root/src/gui

USER root

COPY requirements.txt /opt/app-root/src/gui/

RUN dnf update -y \
 && chown -R default:root /opt/app-root/src/gui

USER default
RUN pip install -r requirements.txt


#USER root
#RUN chmod a+x /opt/app-root/src/gui/run.sh
#USER default

EXPOSE 8501

ENTRYPOINT ["sh", "-c", "streamlit run /opt/app-root/src/gui/ui.py"]