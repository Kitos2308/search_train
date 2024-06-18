import typer

app = typer.Typer()


@app.command()
def start(ctx: typer.Context,app_name:str, chunk_size:int=1000):
    print(f'start {app_name}')


@app.command()
def hello(name: str):
    print(f"Hello {name}")

if __name__=='__main__':
    app()