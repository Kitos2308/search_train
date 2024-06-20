from sqlalchemy import text

source_first_example = (
    text('''
    SELECT 
    concat(entity_id, concat('_', type)) as meta_id, 
    concat(source_txt1, concat(source_txt2,concat(source_txt3,source_txt4))) as text , 
    img, 
    type,
    entity_date  
    FROM source.text_one
'''))