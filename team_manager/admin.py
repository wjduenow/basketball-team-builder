from django.contrib import admin

from .models import Player, Group, GymSlot, Game, GymSlot, GymSession, Team


class GameAdmin(admin.ModelAdmin):
    readonly_fields = ('start_time',)

admin.site.register(Game,GameAdmin)
admin.site.register(Player)
admin.site.register(Group)
admin.site.register(GymSlot)
admin.site.register(GymSession)
admin.site.register(Team)
