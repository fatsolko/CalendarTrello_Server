# first stage
FROM python:3-onbuild

EXPOSE 5000

# make sure you include the -u flag to have our stdout logged
CMD ["python", "server.py"]

