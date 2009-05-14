from django import forms
from django.utils.translation import ugettext_lazy as _
from ponymine.models import Ticket, Project, Membership, Status

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        exclude = ('reported_by',)

    def limit_assignable_users(self, queryset):
        """
        Limits the users who may be assigned a ticket to those who are members
        of a project.
        """
        self.fields['assigned_to'] = forms.ModelChoiceField(queryset=queryset,
                                                            empty_label=None)

class UpdateTicketForm(TicketForm):
    notes = forms.CharField(widget=forms.Textarea, required=False,
                            label=_('Notes'))

    class Meta:
        model = Ticket
        exclude = ('reported_by', 'subject', 'description', 'keywords')

class ChangeStatusForm(forms.Form):
    status = forms.ModelChoiceField(queryset=Status.objects.all(),
                                    empty_label=None)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ('members',)

    def update_parents(self, project):
        """
        Intended to remove `project` from the list of projects that can be used
        as a parent.  This should help stop cyclic project hierarchies.
        """
        if project.id:
            queryset = Project.objects.exclude(id__exact=project.id)
            self.fields['parent'] = forms.ModelChoiceField(queryset=queryset)

class MembershipForm(forms.ModelForm):
    remove = forms.BooleanField(required=False)

    class Meta:
        model = Membership
        exclude = ('project',)
