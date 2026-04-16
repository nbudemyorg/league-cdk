#!/usr/bin/env python3

import aws_cdk as cdk

from league.league_root_stack import LeagueRootStack

app = cdk.App()
LeagueRootStack(
    app,
    'LeagueRootStack',
)

app.synth()
