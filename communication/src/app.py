from raya.application_base import RayaApplicationBase
from raya.exceptions import RayaCommNotRunningApp


class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.i = 0
        self.comm = await self.enable_controller('communication')
        self.comm.create_incoming_msg_listener(callback=self.incoming_msg_callback1)


    def incoming_msg_callback1(self, msg):
        self.log.info(f'Message received:')
        self.log.info(f'  msg: {msg}')
        self.log.info(f'')


    async def loop(self):
        msg = {'other_string': 'hello', 'other_number': self.i}
        self.log.info(f'Sending message to GGS server:')
        self.log.info(f'  {msg}')
        self.log.info(f'')
        try:
            await self.comm.send_msg(msg)
        except RayaCommNotRunningApp:
            self.log.warn('GGS not running yet')
        await self.sleep(5.0)
        self.i += 1


    async def finish(self):
        pass