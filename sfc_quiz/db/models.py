import uuid
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON
from uuid import UUID


class CustomSQLModel(SQLModel):
    class Config:
        arbitrary_types_allowed = True


class Question(CustomSQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4,
                                    primary_key=True,
                                    index=True,
                                    nullable=False)
    question_text: str = Field(default=None, nullable=False)
    no_variables: int = Field(default=None, nullable=True)
    variable_values: str = Field(default=None, nullable=True)
    no_solution_steps: int = Field(default=None, nullable=True)
    solution_params: str = Field(default=None, nullable=True)
    solution_formulas: str = Field(default=None, nullable=True)
    excel_formula: str = Field(default=None, nullable=True)


class TableData(CustomSQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4,
                                    primary_key=True,
                                    index=True,
                                    nullable=False)
    question_id: UUID = Field(default_factory=uuid.uuid4, foreign_key="question.id"),
    data: JSON = Field(default_factory=dict, sa_column=Column(JSON))
