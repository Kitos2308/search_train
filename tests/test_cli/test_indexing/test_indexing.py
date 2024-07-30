import pytest
from dynaconf import settings
from elasticsearch import Elasticsearch
from sqlalchemy.ext.asyncio import AsyncSession
from typer import Typer
from typer.testing import CliRunner

from app.cli.typer_app import get_app
from tests.test_cli.test_indexing.conftest import CursorMock, RowMock

runner = CliRunner()


@pytest.fixture()
def arts_sql_mock() -> CursorMock:
    return CursorMock(
        [
            RowMock(
                {
                    "id": "66735666",
                    "uuid": "a7243cd3-1386-4a00-9250-a58c4fcfe0fd",
                    "title": "Фьючерсные спреды: классификация, анализ, торговля",
                    "type": "4",
                    "first_time_sale_at": "2016-06-09 06:31:16",
                    "art_level": 3,
                    "persons": "Кирилл Перчанок",
                    "isbn": "978-5-04-381092-2, 978-5-04-381092-210",
                    "rating": "",
                    "face_ids": "1 3 10 34",
                    "genre_ids": "154 434 123",
                    "genre_names": "экономика торговля",
                    "library_ids": "15986171 15987656 16030763",
                    "language": "ru",
                    "disallowed_country_codes": "EN RU FR",
                }
            ),
            RowMock(
                {
                    "id": "66735670",
                    "uuid": "7b427353-0dbb-4ee4-b60a-b96c364600be",
                    "title": "Цифровое будущее или экономика?",
                    "type": "4",
                    "first_time_sale_at": "2018-09-09 06:31:16",
                    "art_level": 5,
                    "persons": "Здислав Шиманьский Александр Черновалов",
                    "isbn": "978-5-04-381105-9",
                    "rating": "",
                    "face_ids": "1 2 7",
                    "genre_ids": "154",
                    "genre_names": "",
                    "library_ids": None,
                    "language": "en",
                    "disallowed_country_codes": "",
                }
            ),
            RowMock(
                {
                    "id": "66735694",
                    "uuid": "68071d9e-5fc8-4558-92de-8512fef2a8b4",
                    "title": "История его слуги",
                    "type": "1",
                    "first_time_sale_at": "2022-12-09 06:31:16",
                    "art_level": 1,
                    "persons": "Эдуард Лимонов",
                    "isbn": "978-5-04-379922-7",
                    "rating": "10",
                    "face_ids": "1 5 7",
                    "genre_ids": "5463",
                    "genre_names": "роман",
                    "library_ids": "708693441",
                    "language": "ru",
                    "disallowed_country_codes": "US CA MX BM SE IT HT PR VI NL IN DE IR BO GU AN IE FR HK SG JP AU IL DK MY ES GL NO CL BS AR DM BE BR "
                    "BZ CH ZA AE SA DZ EG MU MA NG GA NA RW MG MR TZ CI GH CD ZW BJ CG MW UG MZ CM NE KE BW AO LR ZM SC LS "
                    "SL KM SD ML BF SZ PT TG LY SN GW QA TN RE CV GQ CF GM TH CN TR UZ PL LU VE NZ PE AT HU GR PK KP BD ID "
                    "PH TW LA AF VN LK NC BN FI ME CZ FO CY UA GE BY IQ AM LB MD BG OM LV KZ EE SK JO BA KW AX AL LT RS RO "
                    "IS CR GP MK MT TJ FK BH AZ MC JM FM EC KY TC HN CO YE BB VG SY NI DO GD GT SV TT WS CK BV FJ PA MH LC "
                    "MP PW KH AS SI KN VC PY SR GY GI PG AG AW IM UY MO AI NP PM BI KG TM HR SM GN MM BT GG TD MQ GF LI SO "
                    "PS ET YT PF JE AD AQ ER MN VU MV GB CU VA DJ SH ST MS SB TV KI TO IO NU TK NF NR KR UM XK SS BL BQ SX",
                }
            ),
            RowMock(
                {
                    "id": "67709575",
                    "uuid": "02d21c3b-dab2-11ec-852b-ac1f6b0b3464",
                    "title": "Как люди видят звуки и слышат цвета? И может ли это помочь нам стать креативнее?",
                    "type": "23",
                    "first_time_sale_at": "2019-08-08 06:31:16",
                    "art_level": 2,
                    "persons": "Студия «Богема»",
                    "isbn": "978-5-04-381115-1",
                    "rating": "",
                    "face_ids": "1 2 7",
                    "genre_ids": "162",
                    "genre_names": "",
                    "library_ids": None,
                    "language": "en",
                    "disallowed_country_codes": "",
                }
            ),
            RowMock(
                {
                    "id": "67709574",
                    "uuid": "02d21c3b-dab2-11ec-852b-ac1f6b0b3463",
                    "title": "Старые машины",
                    "type": "22",
                    "first_time_sale_at": "2017-08-08 06:31:16",
                    "art_level": 3,
                    "persons": "Алёна Гринчевская",
                    "isbn": "978-5-04-381115-2",
                    "rating": "",
                    "face_ids": "1 2 7",
                    "genre_ids": "162",
                    "genre_names": "",
                    "library_ids": None,
                    "language": "en",
                    "disallowed_country_codes": "",
                }
            ),
        ]
    )


def test_add_documents_art_from_sql(
    mocker,
    cli_app: Typer,
    arts_sql_mock: CursorMock,
    search_connection: Elasticsearch,
) -> None:

    mocker.patch.object(
        AsyncSession,
        "execute",
        side_effect=[
            arts_sql_mock,
        ],
    )
    cli_result = runner.invoke(
        cli_app,
        [
            "indexing",
            "start-full-reindex",
        ],
    )

    print('s')