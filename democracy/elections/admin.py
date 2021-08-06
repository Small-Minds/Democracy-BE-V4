from django.contrib import admin

from democracy.elections.models import Ballot, Candidate, Election, Position, Vote

admin.site.register(Election)
admin.site.register(Position)
admin.site.register(Candidate)
admin.site.register(Ballot)
admin.site.register(Vote)
