# logviewer/models.py
from django.db import models

class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    request_data = models.TextField()
    error_code = models.IntegerField()

    def __str__(self):
        return f"Error {self.error_code} at {self.timestamp}"

