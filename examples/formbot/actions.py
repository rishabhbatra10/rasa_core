# -*- coding: utf-8 -*-
from typing import Dict, Text, Any, List, Union, Optional

from rasa_sdk import ActionExecutionRejection
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT


class RestaurantForm(FormAction):
    """Example of a custom form action"""

    def name(self):
        # type: () -> Text
        """Unique identifier of the form"""

        return "restaurant_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["cuisine", "num_people", "outdoor_seating",
                "preferences", "feedback"]

    def slot_mappings(self):
        # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {"cuisine": self.from_entity(entity="cuisine",
                                            not_intent="chitchat"),
                "num_people": [self.from_entity(entity="num_people",
                                                intent=["inform",
                                                        "request_restaurant"]),
                               self.from_entity(entity="number")],
                "outdoor_seating": [self.from_entity(entity="seating"),
                                    self.from_intent(intent='affirm',
                                                     value=True),
                                    self.from_intent(intent='deny',
                                                     value=False)],
                "preferences": [self.from_intent(intent='deny',
                                                 value="no additional "
                                                       "preferences"),
                                self.from_text(not_intent="affirm")],
                "feedback": [self.from_entity(entity="feedback"),
                             self.from_text()]}

    @staticmethod
    def cuisine_db():
        # type: () -> List[Text]
        """Database of supported cuisines"""
        return ["caribbean",
                "chinese",
                "french",
                "greek",
                "indian",
                "italian",
                "mexican"]

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer"""
        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_cuisine(self,
                         value: Text,
                         dispatcher: CollectingDispatcher,
                         tracker: Tracker,
                         domain: Dict[Text, Any]) -> Optional[Text]:
        """Validate cuisine value."""

        if value.lower() in self.cuisine_db():
            # validation succeeded
            return value
        else:
            dispatcher.utter_template('utter_wrong_cuisine', tracker)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return None

    def validate_num_people(self,
                            value: Text,
                            dispatcher: CollectingDispatcher,
                            tracker: Tracker,
                            domain: Dict[Text, Any]) -> Optional[Text]:
        """Validate num_people value."""

        if self.is_int(value) and int(value) > 0:
            return value
        else:
            dispatcher.utter_template('utter_wrong_num_people', tracker)
            # validation failed, set slot to None
            return None

    @staticmethod
    def validate_outdoor_seating(value: Text,
                                 dispatcher: CollectingDispatcher,
                                 tracker: Tracker,
                                 domain: Dict[Text, Any]) -> Any:
        """Validate outdoor_seating value."""

        if isinstance(value, str):
            if 'out' in value:
                # convert "out..." to True
                return True
            elif 'in' in value:
                # convert "in..." to False
                return False
            else:
                dispatcher.utter_template('utter_wrong_outdoor_seating',
                                          tracker)
                # validation failed, set slot to None
                return None

        else:
            # affirm/deny was picked up as T/F
            return value

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        dispatcher.utter_template('utter_submit', tracker)
        return []
