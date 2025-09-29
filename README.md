# DSW Bootstrapping Tool

A lightweight FastAPI + SQLAlchemy tool to browse content from a configured DSW instance, let users select items, and generate a ZIP recipe compatible with [dsw-data-seeder](https://github.com/ds-wizard/engine-tools/tree/develop/packages/dsw-data-seeder). The recipe contains metadata, steps, optional SQL scripts, and files ready for seeding.

## Usage

1. **Install** (preferably in a virtual environment):

```bash
pip install -e .
```

2. **Configure** the application by copying `example.env` to `.env` and updating the variables as needed (PostgreSQL and S3 of your DSW instance).

3**Run** the application:

```bash
./run.sh
```

4. **Access** the web interface at `http://localhost:8000` to browse and select items from the DSW instance.
5. **Generate** the ZIP recipe after making your selections.
6. **Use** the generated ZIP file with the [dsw-data-seeder](https://github.com/ds-wizard/engine-tools/tree/develop/packages/dsw-data-seeder).

## Acknowledgement

<p align="left">
  <img src="https://webcentrum.muni.cz/media/3831863/seda_eosc.png" alt="EOSC CZ Logo" height="90">
</p>

---

This project output was developed with financial contributions from the [EOSC CZ](https://www.eosc.cz/projekty/narodni-podpora-pro-eosc) initiative throught the project **National Repository Platform for Research Data** (CZ.02.01.01/00/23_014/0008787) funded by Programme Johannes Amos Comenius (P JAC) of the Ministry of Education, Youth and Sports of the Czech Republic (MEYS).

---

<p align="left">
  <img src="https://webcentrum.muni.cz/media/3832168/seda_eu-msmt_eng.png" alt="EU and MŠMT Logos" height="90">
</p>

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
