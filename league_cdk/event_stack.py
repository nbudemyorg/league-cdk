from aws_cdk import Stack
from aws_cdk.aws_events import EventBus
from constructs import Construct


class EventStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        bus = EventBus(self, 'LeagueEventBus', event_bus_name='league')

        self.league_bus_arn = bus.event_bus_arn
