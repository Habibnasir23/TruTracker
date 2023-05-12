import unittest
from unittest.mock import mock_open, patch, MagicMock

from app import populate_drop_down_menu, app, db, Saved_Locations, get_lat, get_long, add_saved_location, \
    get_saved_locations


class TestPopulateDropDownMenu(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open,
           read_data="BuildingA, Entrance1\nBuildingA, Entrance2\nBuildingB, Entrance1")
    def test_populate_drop_down_menu(self, mock_file):
        building_dict = {}
        populate_drop_down_menu(building_dict)

        self.assertEqual(building_dict, {"BuildingA": ["Entrance1", "Entrance2"], "BuildingB": ["Entrance1"]})


class TestAddSavedLocation(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_saved_location(self):
        email = "testuser@example.com"
        buildname = "West Campus Suites"
        buildoor = "North"
        savedname = "My Room"
        add_saved_location(email, buildname, buildoor, savedname)
        with app.app_context():
            saved_loc = Saved_Locations.query.filter_by(user_email=email, saved_name=savedname).first()
            self.assertIsNotNone(saved_loc)
            self.assertEqual(saved_loc.building_name, buildname)
            self.assertEqual(saved_loc.door_name, buildoor)
            self.assertEqual(saved_loc.latitude, get_lat(buildname, buildoor))
            self.assertEqual(saved_loc.longitude, get_long(buildname, buildoor))


class TestGetSavedLocations(unittest.TestCase):
    def test_get_saved_locations_with_valid_data(self):
        # Ensure that the function returns the correct location details when the input is valid
        email = "test@example.com"
        savedname = "home"
        mock_loc = MagicMock()
        mock_loc.building_name = "Building A"
        mock_loc.door_name = "Door 1"
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_loc
        with patch.object(Saved_Locations, 'query', return_value=mock_query):
            result = get_saved_locations(email, savedname)
        self.assertEqual(result, {"Building A": "Door 1"})


class TestGetAllSavedLocations(unittest.TestCase):
    def test_get_all_saved_locations_with_valid_data(self):
        # Ensure that the function returns the correct location details when the input is valid
        email = "test@example.com"
        mock_loc_1 = MagicMock()
        mock_loc_1.building_name = "Building A"
        mock_loc_1.door_name = "Door 1"
        mock_loc_1.saved_name = "Home"
        mock_locs = [mock_loc_1]
        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = mock_locs
        from app import Saved_Locations, get_all_saved_locations
        with patch.object(Saved_Locations, 'query', return_value=mock_query):
            result = get_all_saved_locations(email)
        self.assertEqual(result, {"Home": {"building_name": "Building A", "door_name": "Door 1"}})


if __name__ == '__main__':
    unittest.main()
