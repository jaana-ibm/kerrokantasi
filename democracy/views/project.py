
# -*- coding: utf-8 -*-

from rest_framework import permissions
from rest_framework import response
from rest_framework import serializers, viewsets, filters, mixins
import django_filters
from rest_framework import status
from rest_framework.exceptions import ValidationError

from democracy.models import Project, ProjectPhase
from democracy.pagination import DefaultLimitPagination
from democracy.views.utils import TranslatableSerializer, NestedPKRelatedField


class ProjectPhaseSerializer(serializers.ModelSerializer, TranslatableSerializer):
    has_hearings = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()

    class Meta:
        model = ProjectPhase
        fields = ('id', 'description', 'has_hearings', 'is_active', 'ordering', 'schedule', 'title',)

    def get_has_hearings(self, project_phase):
        return project_phase.hearings.exists()

    def to_representation(self, instance):
        self.fields.pop('is_active')
        data = super().to_representation(instance)
        if 'hearing' in self.context:
            data['is_active'] = self.context['hearing'].project_phase_id == instance.pk
        return data

    def create(self, validated_data):
        is_active = validated_data.pop('is_active')
        phase = super().create(validated_data)
        if is_active and 'hearing' in self.context:
            self.context['hearing'].project_phase = phase
        return phase

    def update(self, instance, validated_data):
        is_active = validated_data.pop('is_active')
        phase = super().update(instance, validated_data)
        if is_active and 'hearing' in self.context:
            self.context['hearing'].project_phase = phase
        return phase


class ProjectSerializer(serializers.ModelSerializer, TranslatableSerializer):
    phases = NestedPKRelatedField(queryset=ProjectPhase.objects.all(), many=True, expanded=True, serializer=ProjectPhaseSerializer)

    class Meta:
        model = Project
        fields = ('id', 'title', 'phases')


class ProjectFieldSerializer(serializers.RelatedField):
    """
    Serializer for Project field. A property of other instance.
    """

    def to_representation(self, project):
        return ProjectSerializer(project, context=self.context).data


class ProjectCreateUpdateSerializer(serializers.ModelSerializer, TranslatableSerializer):
    phases = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Project
        fields = ('id', 'title', 'phases')

    def validate_phases(self, data):
        if not self.instance:
            return data
        deleted_phases = self.instance.phases.exclude(pk__in=[p['id'] for p in data if 'id' in p])
        for phase in deleted_phases:
            if phase.hearings.exists():
                raise ValidationError('Can not delete phase which has hearings')
        return data

    # TODO: ordering?
    def create(self, validated_data):
        """
        Create a new project from scratch. Phases are all new too.
        """
        phases_data = validated_data.pop('phases')
        project = super().create(validated_data)
        phases = [self._create_phase(phase, project) for phase in phases_data]
        return project

    def update(self, instance, validated_data):
        """
        Update an existing project and its phases.
        """
        phases_data = validated_data.pop('phases')
        project = super().update(instance, validated_data)
        existing_phases = {phase.pk: phase for phase in project.phases.exclude(deleted=True)}
        new_phases = [self._create_phase(phase, project) for phase in phases_data if phase.get('id') not in existing_phases.keys()]
        updated_phases = [self._update_phase(existing_phases[phase['id']], phase, project) for phase in phases_data if phase.get('id') in existing_phases.keys()]
        # existing phases missing from updated phases are to be deleted
        deleted_phases = set(existing_phases.values()) - set(updated_phases)
        [phase.soft_delete() for phase in deleted_phases]
        return project

    def _create_phase(self, phase_data, project):
        serializer = ProjectPhaseSerializer(data=phase_data, context=self.context)
        serializer.is_valid(raise_exception=True)
        return serializer.save(project=project)

    def _update_phase(self, instance, phase_data, project):
        serializer = ProjectPhaseSerializer(instance=instance, data=phase_data, context=self.context)
        serializer.is_valid(raise_exception=True)
        return serializer.save(project=project)


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    pagination_class = DefaultLimitPagination

