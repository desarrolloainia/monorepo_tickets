class EditTicket:
    def __init__(self, ticket_repository):
        self.ticket_repository = ticket_repository

    def execute(self, ticket_id, title=None, description=None, status=None):
        ticket = self.ticket_repository.get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")

        if title is not None:
            ticket.title = title
        if description is not None:
            ticket.description = description
        if status is not None:
            ticket.status = status

        self.ticket_repository.save(ticket)
