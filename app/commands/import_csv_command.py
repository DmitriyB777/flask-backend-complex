import click
import pandas as pd
from flask.cli import with_appcontext
from sqlalchemy import select
from ..models.group import Group
from ..models.product import Product
from ..models.user import User
from ..models.rights_user import RightsUser
from ..extensions import db 

@click.command("import-csv")
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('user_name')
@click.option('--chunk-size', default=1000, help='Count of lines per commit')
@with_appcontext
def import_csv_command(file_path, user_name, chunk_size):

    query = select(User).filter_by(username=user_name)
    user = db.session.execute(query).scalar_one_or_none()
    print(user)
    if not user:
        click.echo(f"❌ User is not found")
        return

    click.echo(f"🚀 Starting import from {file_path}...")

    cache = {}

    query = select(Group)
    groups = db.session.execute(query).scalars().all()

    for group in groups:
        cache[(group.name, group.parent_id)] = group.id

    try:
        reader = pd.read_csv(file_path, chunksize=chunk_size)

        for i, chunk in enumerate(reader):
            click.echo(f"📦 Processing chunk {i+1}...")

            for _, row in chunk.iterrows():
                row_values = row.values.tolist()
                product_name = row_values[-1]

                group_levels = [str(v).strip() for v in row_values[:-1] if pd.notna(v)]

                current_parent_id = None

                for level_name in group_levels:
                    key = (level_name, current_parent_id)

                    if key in cache:
                        current_parent_id = cache[key]
                    else:
                        new_group = Group(name=level_name, parent_id=current_parent_id)

                        db.session.add(new_group)
                        db.session.flush() 
                        current_parent_id = new_group.id
                        cache[key] = current_parent_id

                        new_rights = RightsUser(user_id = user.id, group_id = new_group.id)
                        
                        db.session.add(new_rights)
                
                if pd.notna(product_name):
                    new_product = Product(name=str(product_name).strip(), group_id=current_parent_id)
                    db.session.add(new_product)

            db.session.commit()
            click.echo(f"✅ Chunk {i+1} committed.")

        click.echo("✨ Import completed successfully!")

    except Exception as e:
        db.session.rollback()
        click.echo(f"❌ Error during import: {e}", err=True)