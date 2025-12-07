from fastapi import HTTPException
from http import HTTPStatus
from src.application.repositories.ingredient_repository import IngredientRepository
from src.application.use_cases.ingredient_use_cases import (
    IngredientCreateUseCase,
    IngredientReadUseCase,
    IngredientUpdateUseCase,
    IngredientDeleteUseCase,
    IngredientListUseCase,
    IngredientListByTypeUseCase,
    IngredientListByAppliesToUseCase,
)
from src.application.dto import (
    IngredientCreateRequest,
    IngredientUpdateRequest,
)
from src.application.exceptions import (
    IngredientNotFoundException,
    IngredientAlreadyExistsException,
    IngredientValidationException,
    IngredientBusinessRuleException,
    AuthenticationException,
)
from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface
from src.entities.ingredient import IngredientType
from src.entities.product import ProductCategory



class IngredientController:
    """
    Ingredient controller that handles HTTP requests.

    In Clean Architecture:
    - This is part of the Interface Adapters layer
    - It handles HTTP-specific concerns
    - It delegates business logic to use cases
    - It converts between HTTP data and application DTOs
    """

    def __init__(self, ingredient_repository: IngredientRepository, presenter: PresenterInterface):
        self.ingredient_repository = ingredient_repository
        self.presenter = presenter
        self.create_use_case = IngredientCreateUseCase(ingredient_repository)
        self.read_use_case = IngredientReadUseCase(ingredient_repository)
        self.update_use_case = IngredientUpdateUseCase(ingredient_repository)
        self.delete_use_case = IngredientDeleteUseCase(ingredient_repository)
        self.list_use_case = IngredientListUseCase(ingredient_repository)
        self.list_by_type_use_case = IngredientListByTypeUseCase(ingredient_repository)
        self.list_by_applies_to_use_case = IngredientListByAppliesToUseCase(ingredient_repository)

    def create_ingredient(self, ingredient_data: dict, login: str) -> dict:
        """Create a new ingredient"""
        if not login:
            error_response = self.presenter.present_error(
                AuthenticationException("Authentication required")
            )
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=error_response
            )

        try:
            request = IngredientCreateRequest(
                name=ingredient_data.get("name", ""),
                price=ingredient_data.get("price", 0.0),
                is_active=ingredient_data.get("is_active", True),
                type=ingredient_data.get("type"),
                applies_to_burger=ingredient_data.get("applies_to_burger", False),
                applies_to_side=ingredient_data.get("applies_to_side", False),
                applies_to_drink=ingredient_data.get("applies_to_drink", False),
                applies_to_dessert=ingredient_data.get("applies_to_dessert", False),
            )
            response = self.create_use_case.execute(request)
            return self.presenter.present(response)
        except (
            IngredientAlreadyExistsException,
            IngredientBusinessRuleException,
            IngredientValidationException,
        ) as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=error_response
            )

    def get_ingredient(self, ingredient_internal_id: int, login: str, include_inactive: bool = False) -> dict:
        """Get an ingredient by ID"""
        if not login:
            error_response = self.presenter.present_error(
                AuthenticationException("Authentication required")
            )
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=error_response
            )

        try:
            response = self.read_use_case.execute(ingredient_internal_id, include_inactive=include_inactive)
            return self.presenter.present(response)
        except IngredientNotFoundException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)

    def update_ingredient(self, ingredient_data: dict, login: str) -> dict:
        """Update an ingredient"""
        if not login:
            error_response = self.presenter.present_error(
                AuthenticationException("Authentication required")
            )
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=error_response
            )

        try:
            request = IngredientUpdateRequest(
                internal_id=ingredient_data.get("internal_id"),
                name=ingredient_data.get("name", ""),
                price=ingredient_data.get("price", 0.0),
                is_active=ingredient_data.get("is_active", True),
                type=ingredient_data.get("type"),
                applies_to_burger=ingredient_data.get("applies_to_burger", False),
                applies_to_side=ingredient_data.get("applies_to_side", False),
                applies_to_drink=ingredient_data.get("applies_to_drink", False),
                applies_to_dessert=ingredient_data.get("applies_to_dessert", False),
            )
            response = self.update_use_case.execute(request)
            return self.presenter.present(response)
        except IngredientNotFoundException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)
        except (
            IngredientAlreadyExistsException,
            IngredientBusinessRuleException,
            IngredientValidationException,
        ) as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=error_response
            )

    def delete_ingredient(self, ingredient_internal_id: int, login: str) -> dict:
        """Delete an ingredient"""
        if not login:
            error_response = self.presenter.present_error(
                AuthenticationException("Authentication required")
            )
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=error_response
            )

        try:
            success = self.delete_use_case.execute(ingredient_internal_id)
            return self.presenter.present(
                {"success": success, "message": "Ingredient soft deleted successfully"}
            )
        except IngredientNotFoundException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)

    def list_ingredients(self, login: str, include_inactive: bool = False) -> dict:
        """List all ingredients"""
        if not login:
            error_response = self.presenter.present_error(
                AuthenticationException("Authentication required")
            )
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=error_response
            )

        try:
            response = self.list_use_case.execute(include_inactive=include_inactive)
            return self.presenter.present(response)
        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error_response
            )

    def list_ingredients_by_type(self, type: IngredientType, login: str, include_inactive: bool = False) -> dict:
        """List ingredients by type"""
        if not login:
            error_response = self.presenter.present_error(
                AuthenticationException("Authentication required")
            )
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=error_response
            )

        try:
            response = self.list_by_type_use_case.execute(type, include_inactive=include_inactive)
            return self.presenter.present(response)
        except IngredientNotFoundException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)

    def list_ingredients_by_applies_to(
        self,
        category: ProductCategory,
        login: str,
        include_inactive: bool = False,
    ) -> dict:
        """List ingredients by applies to"""
        if not login:
            error_response = self.presenter.present_error(
                AuthenticationException("Authentication required")
            )
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=error_response
            )

        try:
            response = self.list_by_applies_to_use_case.execute(
                category, include_inactive=include_inactive
            )
            return self.presenter.present(response)
        except IngredientNotFoundException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)

    def list_ingredient_types(self, login: str) -> dict:
        """List all ingredient types"""
        if not login:
            error_response = self.presenter.present_error(
                AuthenticationException("Authentication required")
            )
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=error_response
            )

        try:
            # Get all ingredient types from the enum
            ingredient_types = [{"value": ingredient_type.value, "name": ingredient_type.name} 
                              for ingredient_type in IngredientType]
            return {"ingredient_types": ingredient_types, "total_count": len(ingredient_types)}
        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error_response
            )