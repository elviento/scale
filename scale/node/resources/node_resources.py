"""Defines the class that represents a set of resources on a node"""
from __future__ import unicode_literals

from util.exceptions import ScaleLogicBug


class NodeResources(object):
    """This class encapsulates a set of node resources
    """

    def __init__(self, resources):
        """Constructor

        :param resources: The list of node resources
        :type resources: list
        """

        self._resources = {}  # {Name: Resource}
        for resource in resources:
            if resource.resource_type != 'SCALAR':
                raise ScaleLogicBug('Resource type "%s" is not currently supported', resource.resource_type)
            self._resources[resource.name] = resource

    @property
    def resources(self):
        """The list of resources

        :returns: The list of resources
        :rtype: list
        """

        return self._resources.values()

    def add(self, node_resources):
        """Adds the given resources

        :param node_resources: The resources to add
        :type node_resources: :class:`node.resources.NodeResources`
        """

        for resource in node_resources.resources:
            if resource.name in self._resources:
                self._resources[resource.name].value += resource.value  # Assumes SCALAR type
            else:
                self._resources[resource.name] = resource.copy()

    def generate_status_json(self, resource_dict):
        """Generates the portion of the status JSON that describes these resources

        :param resource_dict: The dict for these resources
        :type resource_dict: dict
        """

        for resource in self._resources.values():
            resource_dict[resource.name] = resource.value  # Assumes SCALAR type

    def increase_up_to(self, node_resources):
        """Increases each resource up to the value in the given node resources

        :param node_resources: The resources
        :type node_resources: :class:`node.resources.NodeResources`
        """

        for resource in node_resources.resources:
            if resource.name in self._resources:
                if self._resources[resource.name].value < resource.value:  # Assumes SCALAR type
                    self._resources[resource.name].value = resource.value
            else:
                self._resources[resource.name] = resource.copy()

    def is_equal(self, node_resources):
        """Indicates if these resources are equal. This should be used for testing only.

        :param node_resources: The resources to compare
        :type node_resources: :class:`node.resources.NodeResources`
        :returns: True if these resources are equal, False otherwise
        :rtype: bool
        """

        # Make sure they have the exact same set of resource names
        names = set()
        for resource in node_resources.resources:
            names.add(resource.name)
        if self._resources.keys() != names:
            return False

        for resource in node_resources.resources:
            if round(self._resources[resource.name].value, 5) != round(resource.value, 5):  # Assumes SCALAR type
                return False

        return True

    def is_sufficient_to_meet(self, node_resources):
        """Indicates if these resources are sufficient to meet the requested resources

        :param node_resources: The requested resources
        :type node_resources: :class:`node.resources.NodeResources`
        :returns: True if these resources are sufficient for the request, False otherwise
        :rtype: bool
        """

        for resource in node_resources.resources:
            if resource.name not in self._resources:
                return False
            if self._resources[resource.name].value < resource.value:  # Assumes SCALAR type
                return False

        return True

    def subtract(self, node_resources):
        """Subtracts the given resources

        :param node_resources: The resources to subtract
        :type node_resources: :class:`node.resources.NodeResources`
        """

        for resource in node_resources.resources:
            if resource.name in self._resources:
                self._resources[resource.name].value -= resource.value  # Assumes SCALAR type

    def to_logging_string(self):
        """Converts the resource to a readable logging string

        :returns: A readable string for logging
        :rtype: string
        """

        logging_str = ', '.join(['%.2f %s' % (resource.value, resource.name) for resource in self._resources.values()])
        return '[%s]' % logging_str
