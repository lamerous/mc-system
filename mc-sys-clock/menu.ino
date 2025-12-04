Menu::Menu(GyverOLED<SSD1306_128x64>* oled_ptr) {
  this->oled = oled_ptr;
  this->cur_item = 0;
  this->max_items = 0;
  this->home_pos_x = 0;
  this->home_pos_y = 0;
  this->items = nullptr;
  this->messages = nullptr;
}

Menu::~Menu() {
  if (items != nullptr) {
    delete[] items;
    items = nullptr;
  }
}

void Menu::selectNext() {
  cur_item++;
  if (cur_item >= max_items) {
    cur_item = 0;
  }
}

void Menu::addItem(String item, String message) {
  String* new_items = new String[max_items + 1];
  String* new_messages = new String[max_items + 1];

  for (int i = 0; i < max_items; i++) {
    new_items[i] = items[i];
    new_messages[i] = messages[i];
  }
  
  new_items[max_items] = item;
  new_messages[max_items] = message;

  if (items != nullptr) {
    delete[] items;
  }
  if (messages != nullptr) {
    delete[] messages;
  }

  items = new_items;
  messages = new_messages;
  max_items++;
}

void Menu::changeItemName(int ind, String item) {
  items[ind] = item;
}

void Menu::setHomePos(int x, int y) {
  this->home_pos_x = x;
  this->home_pos_y = y;
}

void Menu::draw() {
  if (oled == nullptr) return;
  
  for (int i = 0; i < max_items; i++) {
    if (cur_item == i) {
      oled->rect(home_pos_x+0, home_pos_y+i*8, home_pos_x+128, home_pos_y+i*8+7, OLED_FILL);
      oled->invertText(true);
    }

    oled->setCursorXY(home_pos_x+0, home_pos_y+i*8);
    oled->print(items[i]);
    oled->invertText(false);
  }
}

void Menu::draw_message(){
  oled->autoPrintln(1);
  oled->clear();
  oled->setCursorXY(home_pos_x, home_pos_y);

  oled->print(messages[cur_item]);

  drawHeader();

  oled->update();
  oled->autoPrintln(0);
}

int Menu::getCurItem(){
  return this->cur_item;
}