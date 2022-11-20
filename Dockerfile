FROM iisas/hadoop-spark-pig-hive:2.9.2

RUN mkdir -p /labs && chmod -R a+rwx /labs/
WORKDIR /labs
RUN mkdir /.local && chmod a+rwx /.local

CMD ["/bin/bash"]