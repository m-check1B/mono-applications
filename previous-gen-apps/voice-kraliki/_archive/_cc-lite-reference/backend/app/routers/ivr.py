"""IVR router - FastAPI endpoints for IVR management"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import uuid4
from typing import List
from app.core.database import get_db
from app.dependencies import get_current_user, require_supervisor
from app.core.logger import get_logger
from app.models.user import User
from app.models.ivr import IVRConfig, IVRMenu, IVRMenuOption, IVRFlow, IVRFlowStep
from app.schemas.ivr import (
    IVRConfigResponse, IVRConfigUpdate,
    IVRMenuCreate, IVRMenuUpdate, IVRMenuResponse,
    IVRFlowCreate, IVRFlowResponse,
    IVRMenuOptionResponse
)

router = APIRouter(prefix="/api/ivr", tags=["ivr"])
logger = get_logger(__name__)


@router.get("/config", response_model=IVRConfigResponse)
async def get_ivr_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get IVR configuration for organization

    **Protected**: Requires authentication
    """
    try:
        # Get or create config
        stmt = (
            select(IVRConfig)
            .where(IVRConfig.organization_id == current_user.organization_id)
            .options(
                selectinload(IVRConfig.main_menu).selectinload(IVRMenu.options)
            )
        )
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()

        if not config:
            # Create default config
            config = IVRConfig(
                id=str(uuid4()),
                organization_id=current_user.organization_id,
                settings={},
                active=True
            )
            db.add(config)
            await db.commit()
            await db.refresh(config)

        return config

    except Exception as e:
        logger.error(f"Error getting IVR config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve IVR configuration"
        )


@router.put("/config", response_model=dict, dependencies=[Depends(require_supervisor)])
async def update_ivr_config(
    update_data: IVRConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update IVR configuration

    **Protected**: Requires supervisor role
    """
    try:
        stmt = select(IVRConfig).where(IVRConfig.organization_id == current_user.organization_id)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IVR configuration not found"
            )

        # Update fields
        if update_data.main_menu_id is not None:
            # Verify menu exists and belongs to org
            menu_stmt = select(IVRMenu).where(
                IVRMenu.id == update_data.main_menu_id,
                IVRMenu.organization_id == current_user.organization_id
            )
            menu_result = await db.execute(menu_stmt)
            if not menu_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Main menu not found"
                )
            config.main_menu_id = update_data.main_menu_id

        if update_data.settings is not None:
            config.settings = update_data.settings

        await db.commit()
        await db.refresh(config)

        return {
            "success": True,
            "message": "IVR configuration updated",
            "config": {"id": config.id}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating IVR config: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update IVR configuration"
        )


@router.get("/menus", response_model=dict)
async def list_menus(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all IVR menus for organization

    **Protected**: Requires authentication
    """
    try:
        stmt = (
            select(IVRMenu)
            .where(IVRMenu.organization_id == current_user.organization_id)
            .options(selectinload(IVRMenu.options))
            .order_by(IVRMenu.created_at.desc())
        )
        result = await db.execute(stmt)
        menus = result.scalars().all()

        menu_responses = []
        for menu in menus:
            options = [
                IVRMenuOptionResponse(
                    id=opt.id,
                    digit=opt.digit,
                    description=opt.description,
                    action=opt.action,
                    target=opt.target,
                    metadata=opt.metadata_payload
                )
                for opt in menu.options
            ]

            menu_responses.append(IVRMenuResponse(
                id=menu.id,
                name=menu.name,
                greeting=menu.greeting,
                options=options,
                timeout=menu.timeout,
                max_retries=menu.max_retries,
                no_input_action=menu.no_input_action,
                no_input_target=menu.no_input_target,
                invalid_input_action=menu.invalid_input_action,
                invalid_input_target=menu.invalid_input_target,
                active=menu.active,
                created_at=menu.created_at,
                updated_at=menu.updated_at
            ))

        return {"menus": menu_responses}

    except Exception as e:
        logger.error(f"Error listing IVR menus: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve IVR menus"
        )


@router.post("/menus", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_supervisor)])
async def create_menu(
    menu_data: IVRMenuCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new IVR menu

    **Protected**: Requires supervisor role
    """
    try:
        # Create menu
        menu_id = str(uuid4())
        menu = IVRMenu(
            id=menu_id,
            organization_id=current_user.organization_id,
            name=menu_data.name,
            greeting=menu_data.greeting,
            timeout=menu_data.timeout,
            max_retries=menu_data.max_retries,
            no_input_action=menu_data.no_input_action,
            no_input_target=menu_data.no_input_target,
            invalid_input_action=menu_data.invalid_input_action,
            invalid_input_target=menu_data.invalid_input_target,
            active=True
        )
        db.add(menu)

        # Create options
        for option_data in menu_data.options:
            option = IVRMenuOption(
                id=str(uuid4()),
                menu_id=menu_id,
                digit=option_data.digit,
                description=option_data.description,
                action=option_data.action,
                target=option_data.target,
                metadata_payload=option_data.metadata
            )
            db.add(option)

        await db.commit()
        await db.refresh(menu)

        return {
            "success": True,
            "message": "IVR menu created",
            "menu": {"id": menu.id, "name": menu.name}
        }

    except Exception as e:
        logger.error(f"Error creating IVR menu: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create IVR menu"
        )


@router.put("/menus/{menu_id}", response_model=dict, dependencies=[Depends(require_supervisor)])
async def update_menu(
    menu_id: str,
    menu_data: IVRMenuUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update IVR menu

    **Protected**: Requires supervisor role
    """
    try:
        stmt = (
            select(IVRMenu)
            .where(
                IVRMenu.id == menu_id,
                IVRMenu.organization_id == current_user.organization_id
            )
            .options(selectinload(IVRMenu.options))
        )
        result = await db.execute(stmt)
        menu = result.scalar_one_or_none()

        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IVR menu not found"
            )

        # Update basic fields
        if menu_data.name is not None:
            menu.name = menu_data.name
        if menu_data.greeting is not None:
            menu.greeting = menu_data.greeting
        if menu_data.timeout is not None:
            menu.timeout = menu_data.timeout
        if menu_data.max_retries is not None:
            menu.max_retries = menu_data.max_retries
        if menu_data.no_input_action is not None:
            menu.no_input_action = menu_data.no_input_action
        if menu_data.no_input_target is not None:
            menu.no_input_target = menu_data.no_input_target
        if menu_data.invalid_input_action is not None:
            menu.invalid_input_action = menu_data.invalid_input_action
        if menu_data.invalid_input_target is not None:
            menu.invalid_input_target = menu_data.invalid_input_target

        # Update options if provided
        if menu_data.options is not None:
            # Delete existing options
            for option in menu.options:
                await db.delete(option)

            # Create new options
            for option_data in menu_data.options:
                option = IVRMenuOption(
                    id=str(uuid4()),
                    menu_id=menu_id,
                    digit=option_data.digit,
                    description=option_data.description,
                    action=option_data.action,
                    target=option_data.target,
                    metadata_payload=option_data.metadata
                )
                db.add(option)

        await db.commit()

        return {
            "success": True,
            "message": "IVR menu updated",
            "menu": {"id": menu.id}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating IVR menu: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update IVR menu"
        )


@router.delete("/menus/{menu_id}", response_model=dict, dependencies=[Depends(require_supervisor)])
async def delete_menu(
    menu_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete IVR menu

    **Protected**: Requires supervisor role
    """
    try:
        stmt = select(IVRMenu).where(
            IVRMenu.id == menu_id,
            IVRMenu.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        menu = result.scalar_one_or_none()

        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IVR menu not found"
            )

        await db.delete(menu)
        await db.commit()

        return {
            "success": True,
            "message": "IVR menu deleted"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting IVR menu: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete IVR menu"
        )


@router.post("/flows", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_supervisor)])
async def create_flow(
    flow_data: IVRFlowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create IVR flow

    **Protected**: Requires supervisor role
    """
    try:
        # Verify start menu exists
        menu_stmt = select(IVRMenu).where(
            IVRMenu.id == flow_data.start_menu_id,
            IVRMenu.organization_id == current_user.organization_id
        )
        menu_result = await db.execute(menu_stmt)
        if not menu_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Start menu not found"
            )

        # Create flow
        flow_id = str(uuid4())
        flow = IVRFlow(
            id=flow_id,
            organization_id=current_user.organization_id,
            name=flow_data.name,
            description=flow_data.description,
            start_menu_id=flow_data.start_menu_id,
            active=True
        )
        db.add(flow)

        # Create steps
        for idx, step_data in enumerate(flow_data.steps):
            step = IVRFlowStep(
                id=str(uuid4()),
                flow_id=flow_id,
                step_type=step_data.type,
                target=step_data.target,
                conditions=step_data.conditions,
                order=idx
            )
            db.add(step)

        await db.commit()
        await db.refresh(flow)

        return {
            "success": True,
            "message": "IVR flow created",
            "flow": {"id": flow.id, "name": flow.name}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating IVR flow: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create IVR flow"
        )


@router.get("/flows", response_model=dict)
async def list_flows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all IVR flows for organization

    **Protected**: Requires authentication
    """
    try:
        stmt = (
            select(IVRFlow)
            .where(IVRFlow.organization_id == current_user.organization_id)
            .order_by(IVRFlow.created_at.desc())
        )
        result = await db.execute(stmt)
        flows = result.scalars().all()

        flow_responses = [
            IVRFlowResponse(
                id=flow.id,
                organization_id=flow.organization_id,
                name=flow.name,
                description=flow.description,
                start_menu_id=flow.start_menu_id,
                active=flow.active,
                created_at=flow.created_at,
                updated_at=flow.updated_at
            )
            for flow in flows
        ]

        return {"flows": flow_responses}

    except Exception as e:
        logger.error(f"Error listing IVR flows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve IVR flows"
        )
