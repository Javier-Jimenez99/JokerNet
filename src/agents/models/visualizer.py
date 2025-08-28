from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class RunParameters(BaseModel):
    """Parameters of the current run."""
    hands: int = Field(..., description="Number of hands remaining.")
    discards: int = Field(..., description="Number of discards remaining.")
    money: int = Field(..., description="Current amount of money.")
    ante: int = Field(..., description="Current ante level.")
    round: int = Field(..., description="Current round within the ante.")
    blind: str = Field(..., description="Name of the current blind.")
    current_score: int = Field(..., description="Current score.")
    objective_score: int = Field(..., description="Score needed to win.")

class Joker(BaseModel):
    """Represents a Joker card currently in play."""
    name: str = Field(..., description="The name of the Joker as visible on screen.")

class ShopItem(BaseModel):
    """Represents an item available for purchase in the shop."""
    name: str = Field(..., description="The name of the item as visible in the shop.")
    price: int = Field(..., description="The cost to purchase this item.")
    item_type: Literal['Joker', 'Booster Pack', 'Voucher', 'Other'] = Field(..., description="The type of item available for purchase.")

class PickedHand(BaseModel):
    """Represents the complete picked hand with cards, hand type, and values."""
    picked_cards: Optional[List[str]] = Field(None, description="A list of all cards selected for play (visually shifted upwards). If unable to identify individual picked cards after careful examination, this can be null while still providing hand_type, level, chips, and bonus.")
    correct_picked_cards: bool = Field(..., description="Whether the picked cards correspond with the hand type, correcly."),
    hand_type: str = Field(..., description="The type of poker hand formed by the picked cards (e.g., 'High Card', 'Pair', 'Two Pair', 'Three of a Kind', 'Straight', 'Flush', 'Full House', 'Four of a Kind', 'Straight Flush', 'Royal Flush').")
    level: int = Field(..., description="The level of the hand type (e.g., 'lvl.1', 'lvl.2', etc.). Extract the number only.")
    chips: int = Field(..., description="The base chips value (blue number) for this hand type.")
    bonus: int = Field(..., description="The bonus multiplier (red number) for this hand type.")

class HighlightedElement(BaseModel):
    """Represents the single element highlighted by the cursor."""
    type: Literal['Card', 'Joker', 'ShopItem', 'Button', 'Unknown'] = Field(..., description="The type of the highlighted element.")
    name: str = Field(..., description="The name of the highlighted item.")
    description: Optional[str] = Field(None, description="A brief description, if applicable.")

class GamepadButton(BaseModel):
    """Represents a button that can be activated with a gamepad key."""
    name: str = Field(..., description="The name of the button as visible on screen.")
    gamepad_key: str = Field(..., description="The gamepad key that activates this button (e.g., 'A', 'B', 'X', 'Y', 'LB', 'RB', 'START', 'SELECT').")

class PlayArea(BaseModel):
    """Represents the player's hand and selected cards."""
    hand: List[str] = Field(..., description="A list of all cards currently in the player's hand.")
    picked_hand: Optional[PickedHand] = Field(..., description="The complete picked hand information including cards, hand type, level, chips, and bonus. Present when a hand evaluation is visible, even if individual picked cards cannot be identified.")

class GameState(BaseModel):
    """The overall structured summary of the game state from a screenshot."""
    summary: str = Field(..., description="A concise summary of the current game state, what's happening on screen, and key elements visible.")
    screen: Literal['Menu', 'Shop', 'Play'] = Field(..., description="The type of screen currently displayed.")
    run_parameters: RunParameters = Field(..., description="The current parameters of the run.")
    jokers: List[Joker] = Field(..., description="A list of all Jokers currently in play (visible at the top of the game area).")
    shop_items: List[ShopItem] = Field(default_factory=list, description="A list of all items available for purchase in the shop (only present when in Shop screen).")
    gamepad_buttons: List[GamepadButton] = Field(..., description="A list of buttons that can be activated with gamepad keys, showing both the button name and the associated gamepad key.")
    highlighted_element: HighlightedElement = Field(..., description="The single element currently under the cursor's focus.")
    play_area: PlayArea = Field(..., description="The player's hand and picked hand information.")
    execution_progression: str = Field(None, description="Description and summary of previous game states. It should contain a comparison with the previous one to understand the complete execution.")