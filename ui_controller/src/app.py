from raya.application_base import RayaApplicationBase
from raya.enumerations import MODAL_TYPE, THEME_TYPE

class RayaApplication(RayaApplicationBase):

    async def setup(self):
        self.UI = await self.enable_controller('ui')
        self.i = 0

        #await self.UI.display_screen(title="Hey Tamta!", subtitle="sajdsajda", content="asdsadsadsa")
        await self.UI.display_action_screen(title="Hey Guy!", subtitle="Good morning", button_text="Let's start", theme=THEME_TYPE.DARK)
        #response = await self.UI.display_input_modal(title="Yes", subtitle="asdsadsa", submit_text="Yes", cancel_text="No")
        #response = await self.UI.display_modal(title="SADsdsadas", subtitle="asdsadsda", modal_type=MODAL_TYPE.ERROR)

        data = [{'id': 1, 'name': 'Martin'}, {'id': 2, 'name': 'Alon'}, {'id': 3, 'name': 'Nitsan'}]

        response = await self.UI.display_choice_selector(title="Which one?", show_back_button=False, data=data)

        if response["selected_option"]["id"] == 2:
            response = await self.UI.display_modal(title="SADsdsadas", subtitle="asdsadsda", modal_type=MODAL_TYPE.SUCCESS)


    async def loop(self):   
        self.log.info('Loop')
        await self.sleep(0.5)
        self.i += 1
        if self.i==10:
            self.finish_app()


    async def finish(self):
        self.log.info('App finished')

