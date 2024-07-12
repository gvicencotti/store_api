from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import UUID4
from datetime import datetime
from store.core.exceptions import NotFoundException

from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.usecases.product import ProductUsecase

router = APIRouter(tags=["products"])


@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def post(
    body: ProductIn = Body(...), usecase: ProductUsecase = Depends()
) -> ProductOut:
    try:
        return await usecase.create(body=body)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao inserir o produto")


@router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def get(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> ProductOut:
    try:
        return await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(path="/", status_code=status.HTTP_200_OK)
async def query(usecase: ProductUsecase = Depends()) -> List[ProductOut]:
    return await usecase.query()


@router.patch(path="/{id}", status_code=status.HTTP_200_OK)
async def patch(
    id: UUID4 = Path(alias="id"),
    body: ProductUpdate = Body(...),
    usecase: ProductUsecase = Depends(),
) -> ProductUpdateOut:
    try:
        updated_product = await usecase.update(id=id, body=body)
        updated_product.updated_at = datetime.now()  # Atualiza o updated_at para o tempo atual
        return updated_product
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.post(path="/create_different_prices", status_code=status.HTTP_201_CREATED)
async def create_products_with_different_prices(
    products: List[ProductIn] = Body(...), usecase: ProductUsecase = Depends()
) -> List[ProductOut]:
    created_products = []
    for product in products:
        created_product = await usecase.create(body=product)
        created_products.append(created_product)
    return created_products


@router.get(path="/filter_by_price", status_code=status.HTTP_200_OK)
async def filter_products_by_price(
    min_price: float = None, max_price: float = None, usecase: ProductUsecase = Depends()
) -> List[ProductOut]:
    return await usecase.filter_by_price(min_price=min_price, max_price=max_price)
