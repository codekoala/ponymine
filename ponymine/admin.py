from django.contrib import admin
from models import Project, Membership, Role, TicketType, Status, Priority, Component, Ticket

def the_project(obj):
    return obj.project.path()
the_project.short_description = 'Project'

slug_from_name = {'slug': ('name',)}

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'ticket_count', 'date_created', 
                    'is_public', 'is_active')
    search_fields = ('name', 'description', 'homepage')
    list_filter = ('is_public', 'is_active', 'date_created')
    prepopulated_fields = slug_from_name

    def ticket_count(self, project):
        return project.tickets.count()

class MembershipAdmin(admin.ModelAdmin):
    list_display = (the_project, 'user', 'role')

class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = slug_from_name

class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_closed')
    list_filter = ('is_closed',)
    prepopulated_fields = slug_from_name

class PriorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_default')
    prepopulated_fields = slug_from_name

class ComponentAdmin(admin.ModelAdmin):
    list_display = (the_project, 'name')
    prepopulated_fields = slug_from_name

class TicketAdmin(admin.ModelAdmin):
    list_display = (the_project, 'subject', 'reported_by', 'assigned_to', 'is_closed')
    list_filter = ('ticket_type', 'status', 'priority', 'date_created')

admin.site.register(Project, ProjectAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Role, AttributeAdmin)
admin.site.register(TicketType, AttributeAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Priority, PriorityAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Ticket, TicketAdmin)