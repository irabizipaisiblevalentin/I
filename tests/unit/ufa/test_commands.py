"""Tests for UFA command/message bus."""

import pytest
from ufa.commands import MessageBus, Command, Query, CommandResult


class CreateItem(Command):
    pass


class GetItem(Query):
    pass


class TestMessageBus:
    def test_register_and_dispatch_command(self):
        bus = MessageBus()
        bus.register_command(CreateItem, lambda msg: "created")
        result = bus.dispatch(CreateItem())
        assert result.success
        assert result.data == "created"

    def test_register_and_dispatch_query(self):
        bus = MessageBus()
        bus.register_query(GetItem, lambda msg: {"id": 1})
        result = bus.dispatch(GetItem())
        assert result.success
        assert result.data == {"id": 1}

    def test_no_handler(self):
        bus = MessageBus()
        result = bus.dispatch(CreateItem())
        assert not result.success
        assert "no handler" in result.errors[0]

    def test_command_result_return(self):
        bus = MessageBus()
        bus.register_command(CreateItem,
                            lambda msg: CommandResult(True, data="ok"))
        result = bus.dispatch(CreateItem())
        assert result.data == "ok"

    def test_handler_exception(self):
        bus = MessageBus()
        bus.register_command(CreateItem, lambda msg: 1 / 0)
        result = bus.dispatch(CreateItem())
        assert not result.success
        assert "zero" in result.errors[0].lower()

    def test_dispatch_count(self):
        bus = MessageBus()
        bus.register_command(CreateItem, lambda msg: None)
        bus.dispatch(CreateItem())
        bus.dispatch(CreateItem())
        assert bus.dispatch_count == 2

    def test_behavior(self):
        bus = MessageBus()
        order = []
        bus.register_behavior(lambda msg, next: (order.append("b"), next()))
        bus.register_command(CreateItem, lambda msg: order.append("h"))
        bus.dispatch(CreateItem())
        assert "b" in order
        assert "h" in order

    def test_has_handler(self):
        bus = MessageBus()
        assert not bus.has_handler(CreateItem)
        bus.register_command(CreateItem, lambda msg: None)
        assert bus.has_handler(CreateItem)

    def test_dispatch_many(self):
        bus = MessageBus()
        bus.register_command(CreateItem, lambda msg: "ok")
        results = bus.dispatch_many([CreateItem(), CreateItem()])
        assert len(results) == 2

    def test_handler_count(self):
        bus = MessageBus()
        bus.register_command(CreateItem, lambda msg: None)
        bus.register_query(GetItem, lambda msg: None)
        assert bus.handler_count() == 2

    def test_clear(self):
        bus = MessageBus()
        bus.register_command(CreateItem, lambda msg: None)
        bus.clear()
        assert bus.handler_count() == 0

    def test_elapsed_ms(self):
        bus = MessageBus()
        bus.register_command(CreateItem, lambda msg: None)
        result = bus.dispatch(CreateItem())
        assert result.elapsed_ms >= 0
