from api import PetFriends
from settings import *

class TestPetFriends:
    def setup(self):
        self.pf = PetFriends()

    def test_get_api_key_for_valid_user(self, email=valid_email, password=valid_password):
        """Метод протестирует успешность авторизации через API запрос api.py
        Проверит статус-код и наличие в ответе уникального ключа пользователя."""
        status, result = self.pf.get_api_key(email, password)
        assert status == 200
        assert 'key' in result

    def test_get_all_pets_with_valid_key(self, filter=''): 
        """Метод протестирует корректное получение списка питомцев.Проверит статус-код и наличие в ответе
        хотя бы одного массива-карточки"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        status, result = self.pf.get_list_of_pets(auth_key, filter)
        assert status == 200
        assert len(result['pets']) > 0

    def test_add_new_pet_with_valid_data(self, name='Барбоскин', animal_type='двортерьер',
                                         age='4', pet_photo='images/cat1.jpg'):
        """Функция протестирует добавление нового питомца.Проверит статус-код и наличие в ответе имени 
        нового питомца"""
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
        assert status == 200
        assert result['name'] == name

    def test_successful_update_self_pet_info(self, name='Мурзик', animal_type='Котэ', age=5):
            """Функция протестирует алгоритм обновления информации о питомце.Проверит статус-код и наличие
            новой информации в обновлённой карточке (в данном случае - новое имя)"""
            _, auth_key = self.pf.get_api_key(valid_email, valid_password)
            _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

            if len(my_pets['pets']) > 0:
                status, result = self.pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
                assert status == 200
                assert result['name'] == name
            else:
                raise Exception("There is no my pets")
            
    def test_successful_delete_self_pet(self):
        """Функция протестирует удаление питомца с ресурса. Проверит статус-код и отсутствие id удалённого питомца
        в списке собственных питомцев"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        if len(my_pets['pets']) == 0:
            self.pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
            _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        pet_id = my_pets['pets'][0]['id']
        status, _ = self.pf.delete_pet(auth_key, pet_id)
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        assert status == 200
        assert pet_id not in my_pets.values()
    
    def test_successful_add_pet_without_photo(self, name='Лавашик', animal_type='Hot-dog',age='2'):
        """Функция протестирует добавление нового питомца без фото.Проверит статус-код и наличие в ответе
        имени нового питомца"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        status, result = self.pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
        assert status == 200
        assert result['name'] == name
    
    def test_successful_add_pet_photo(self, pet_photo='images\P1040103.jpg'):
        """Функция протестирует добавление фото существующему питомцу через перебор питомцев не имеющих фото.
        Проверит статус-код и наличие фото у обновлённого питомца"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
        pet_id = ""
        if my_pets['pets'][0]['pet_photo'] == "":
            pet_id = my_pets['pets'][0]['id']
        else:
            for pet in my_pets['pets']:
                if pet['pet_photo'] == "":
                    pet_id = pet['id']
                break
        if pet_id != "":
            status, result = self.pf.add_pet_photo(auth_key, pet_id, pet_photo)
            _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")
            assert status == 200
            assert result['pet_photo'] == my_pets['pets'][0]['pet_photo']

        # +10 Тестов далее

    def test_create_pet_with_text_in_age(self, name='Лавашик', animal_type='Hot-dog', age='восемь'):
        """1. Функция протестирует добавление нового питомца с текстом в графе возраста.Проверит тип данных
        заголовка age на содержание числа,если питомец успешно создан"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        status, result = self.pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
        try:
            result['age'] = int(result['age']) # Если питомец создан,то система попробует преобразовать - 
        except ValueError: # - полученное значение age в число
            assert isinstance(result['age'], str) is False # если age не получится перевести в число,значит - 
        # питомец создан с невалидным значением - тест падает (баг)
        else:
            assert status == 200 # если age удалось перевести в число,значит значение питомца валидное

    def test_create_pet_with_number_in_name(self, name='832', animal_type='Hot-dog', age='4'):
        """2. Функция протестирует добавление нового питомца с числом в графе имени.Проведёт преобразование
        значения name и ряд сравнений для анализа"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        status, result = self.pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
        try:
            result['name'] = int(result['name']) #Если питомец создан,то система попробует преобразовать - 
        except ValueError: # - полученное значение name в число
            assert status == 200 # если name не получится перевести в число,значит питомец не создан или - 
        else: # - значение name удовлетворительное  
            assert status == 400 # если name получается перевести в число,значит питомец создан с числом в имени - 
        # - тест падает (баг)

    def test_create_pet_with_number_in_animaltype(self, name='Лавашик', animal_type='248271', age='1'):
        """3. Функция протестирует добавление нового питомца с числом в графе породы.Проведёт преобразование
        значения animal_type и ряд сравнений для анализа"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        status, result = self.pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
        try:
            result['animal_type'] = int(result['animal_type']) #Если питомец создан,то система попробует - 
        except ValueError: # преобразовать полученное значение animal_type в число
            assert status == 200 # если не получится перевести в число,значит питомец не создан или значение удовлетворительное  
        else: 
            assert status == 400 # если получается перевести в число,значит питомец создан с числом в породе - 
        # тест падает (баг)

    def test_delete_alien_pet(self):
        """4. Функция протестирует удаление с ресурса питомца другого пользователя.Проверит,что удаляемый питомец
        не принадлежит пользователю и сравнит ожидаемый статус-код с фактическим.(Тест вызова ошибки)"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        _, another_pets = self.pf.get_list_of_pets(auth_key, "") # получить общий список питомцев
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets") # получить мой список питомцев

        pet_id = another_pets['pets'][3]['id'] # взять случайного питомца из списка
        if pet_id not in my_pets['pets']: # если питомец мне не принадлежит
            status, _ = self.pf.delete_pet(auth_key, pet_id) # пробуем удалить его
            assert status == 403 # ожидается статус,отличный от 200. Вероятно, 403 - не уполномочен для операции.
        else:
            status, _ = self.pf.delete_pet(auth_key, pet_id)
            assert status == 200
            print('Удалён питомец из моего списка. Удалите своих питомцев или смените номер: [pets][???][id]')
        
    def test_add_pet_without_name(self, name='', animal_type='Hot-dog',age='2'):
        """5. Функция протестирует добавление питомца без имени.Сравнит значение name с заголовком name в ответе
        и сравнит ожидаемый статус-код с фактическим.(Тест вызова ошибки)"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        status, result = self.pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
        if len(result['name']) <= 0: # если питомец создан с пустым именем: в name нет символов
            assert status == 400 # ожидается статус,отличный от 200. Вероятно,400/449 - недостаточно информации для запроса.
        elif len(result['name']) >= 1:
            assert status == 200 # Если в name есть символы,то тест проходит
        else:
            assert status == 400 # Если ответ пуст,значит питомца не удалось создать с невалидными данными.
        
    def test_update_info_alien_pet(self, name='Выдра', animal_type='Ароматная', age=2):
        """6. Функция протестирует алгоритм обновления информации чужого питомца.Проверит,что обновляемый питомец
         не принадлежит пользователю и сравнит ожидаемый статус-код с фактическим.(Тест вызова ошибки)"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets") # получить мой список питомцев
        _, another_pets = self.pf.get_list_of_pets(auth_key, "") # получить общий список питомцев

        pet_id = another_pets['pets'][3]['id'] # взять случайного питомца из списка
        if pet_id not in my_pets['pets']: # если питомец мне не принадлежит
            status, result = self.pf.update_pet_info(auth_key, another_pets['pets'][3]['id'], name, animal_type, age) # пробуем обновить его
            assert status == 403 # ожидается статус,отличный от 200. Вероятно, 403 - не уполномочен для операции.
        else:
            raise Exception("Обновлена информация собственного питомца")
            
    def test_create_pet_with_big_values(self, name='ЛавашикЛавашииикЛавашшашашашЛавашик', 
        animal_type='Hot-dog-dog-dog-dog-dog-dog-dog-dog',age='2517295283685629174927465'):
        """7. Функция протестирует добавление нового питомца с невалидно-большими значениями.(Тест вызова ошибки)"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        status, result = self.pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
        assert status == 400 # ожидается статус,отличный от 200. Вероятно, 400/431 - превышена допустимая длина заголовков

    def test_get_api_key_with_invalid_values(self, email=invalid_email, password=invalid_password):
        """8. Функция протестирует возможность авторизации через API запрос api.py с невалидными данными пользователя
        Проверит статус-код.(Тест вызова ошибки)"""
        status, _ = self.pf.get_api_key(email, password)
        assert status == 403 # ожидается статус,отличный от 200. Вероятно, 403 - требуются валидные данные

    def test_add_pet_with_invalid_auth_key(self, name='Лавашик', animal_type='Hot-dog',age='2'):
        """9. Функция протестирует добавление нового питомца c неверным ключом авторизации.(Тест вызова ошибки)"""
        auth_key = {"key": "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"} # чужеродный ключ

        status, result = self.pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
        assert status == 403 # ожидается статус,отличный от 200. Вероятно, 403 - неверный ключ авторизации.

    def test_delete_self_pet_with_invalid_auth_key(self):
        """10. Функция протестирует удаление питомца с ресурса c неверным ключом авторизации.(Тест вызова ошибки)"""
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        invalid_auth_key = {"key": "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"} # используется в тесте
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets") # используется косвенно

        if len(my_pets['pets']) == 0: # создаст питомца,если их нет,используя верный ключ
            self.pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
            _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")
        pet_id = my_pets['pets'][0]['id']
        status, _ = self.pf.delete_pet(invalid_auth_key, pet_id) # пробуем удалить с неверным ключом
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        assert status == 403 # ожидается статус,отличный от 200. Вероятно, 403 - неверный ключ авторизации.