FROM coady/pylucene


COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN mkdir -p /labs && chmod -R a+rwx /labs/
WORKDIR /labs
RUN mkdir /.local && chmod a+rwx /.local

CMD [ "tail", "-f", "/dev/null" ]