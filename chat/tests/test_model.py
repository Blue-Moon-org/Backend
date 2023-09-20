from chat.tests.test_setup import TestSetUp
from chat.models import Chatroom, Request, Message


class TestModel(TestSetUp):

	def test_create_chatroom(self):
		user = self.register_user()
		chatroom = Chatroom.objects.create(name="legend")
		chatroom.users.add(user)
		self.assertIsInstance(chatroom, Chatroom)
		self.assertEqual(str(chatroom), str(chatroom.id))

	def test_create_request(self):
		user = self.register_user()
		chatroom = Chatroom.objects.create(name="legend")
		chatroom.users.add(user)
		request = Request.objects.create(user=user, chatroom=chatroom)
		self.assertIsInstance(request, Request)


	def test_create_message(self):
		user = self.register_user()
		chatroom = Chatroom.objects.create(name="legend")
		chatroom.users.add(user)
		msg = Message.objects.create(user=user, chatroom=chatroom, body="This is the body of the chat")
		#self.assertEqual(str(history), "example")
		self.assertIsInstance(msg, Message)
		self.assertEqual(str(msg), str(msg.id))
		#self.assertEqual(msg.characters, 1)