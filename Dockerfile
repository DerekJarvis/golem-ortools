FROM docsaintly/python-ortools:2
COPY run.sh /golem/entrypoints/
VOLUME /golem/work /golem/output /golem/resource
