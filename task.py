from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task, Comment, User,Notification
from notification import send_notification
import logging
from datetime import datetime

bp = Blueprint('routes', __name__)

@bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)  

        if page < 1 or per_page < 1:
            return jsonify({'error': 'Page and per_page must be greater than 0'}), 422

        tasks = Task.query.paginate(page=page, per_page=per_page)
        task_list = [
            {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'priority': task.priority,
                'completion_percentage': task.completion_percentage,
                'status': task.status,  
                'comments': [{'id': comment.id, 'content': comment.content} for comment in task.comments]
            } for task in tasks.items
        ]

        return jsonify({
            'tasks': task_list,
            'total': tasks.total,
            'pages': tasks.pages,
            'current_page': tasks.page
        })
    except Exception as e:
        logging.error(f"Error fetching tasks: {str(e)}")
        return jsonify({'error': 'Error fetching tasks'}), 500

@bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task_detail(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        
        assigned_user = User.query.get(task.assigned_to) if task.assigned_to else None
        assigned_user_email = assigned_user.email if assigned_user else None
        
        task_detail = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'priority': task.priority,
            'completion_percentage': task.completion_percentage,
            'status': task.status,  
            'assigned_to_email': assigned_user_email  
        }

        comments = Comment.query.filter_by(task_id=task_id).all()
        comment_list = [
            {
                'id': comment.id,
                'content': comment.content,
                'user_id': comment.user_id,
                'created_at': comment.created_at.isoformat()
            } for comment in comments
        ]

        return jsonify({'task': task_detail, 'comments': comment_list})

    except Exception as e:
        logging.error(f"Error fetching task detail for Task {task_id}: {str(e)}")
        return jsonify({'error': 'Error fetching task detail'}), 500


@bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        if 'title' not in data or not data['title']:
            return jsonify({'error': 'Title is required'}), 400

        assigned_user_id = user_id

        assigned_to_email = data.get('assigned_to_email')

        if assigned_to_email:
            assigned_user = User.query.filter_by(email=assigned_to_email).first()

            if not assigned_user:
                return jsonify({'error': 'User with the provided email does not exist'}), 404
            else:
                assigned_user_id = assigned_user.id
                notification_message = f"You have been assigned a new task: {data['title']}"
                send_notification(assigned_to_email, "New Task Assigned", notification_message)

                new_notification = Notification(
                    user_id=assigned_user_id,  
                    message=notification_message
                )

                db.session.add(new_notification)

        due_date = None
        if 'due_date' in data and data['due_date']:
            try:
                due_date = datetime.fromisoformat(data['due_date'])  # Parse only if provided
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        new_task = Task(
            title=data['title'],
            description=data.get('description', ''),
            due_date=due_date,
            priority=data.get('priority', 'normal'),
            completion_percentage=data.get('completion_percentage', 0),
            status=data.get('status', 'To Do'),  
            assigned_to=assigned_user_id  
        )

        db.session.add(new_task)
        db.session.commit()
        logging.info(f"Task {new_task.id} created by User {user_id} and assigned to User {assigned_user_id}")

        return jsonify({'message': 'Task created', 'task_id': new_task.id}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating task: {str(e)}")
        return jsonify({'error': str(e)}), 400  # Return full error for debugging


@bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()

        logging.info(f"Received status: {data.get('status')}")  # Log the received status

        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)

        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date'])

        task.priority = data.get('priority', task.priority)
        task.completion_percentage = data.get('completion_percentage', task.completion_percentage)
        task.status = data.get('status', task.status)  # Update status if provided

        db.session.commit()
        logging.info(f"Task {task_id} updated by User {get_jwt_identity()}")
        return jsonify({'message': 'Task updated'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating task {task_id}: {str(e)}")
        return jsonify({'error': 'Error updating task'}), 500

@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        logging.info(f"Task {task_id} deleted by User {get_jwt_identity()}")
        return jsonify({'message': 'Task deleted'}), 204

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting task {task_id}: {str(e)}")
        return jsonify({'error': 'Error deleting task'}), 500

@bp.route('/tasks/<int:task_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(task_id):
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        if 'content' not in data or not data['content']:
            return jsonify({'error': 'Content is required'}), 400

        new_comment = Comment(
            content=data['content'],
            user_id=user_id,
            task_id=task_id
        )
        db.session.add(new_comment)
        db.session.commit()
        logging.info(f"Comment added to Task {task_id} by User {user_id}")

        return jsonify({'message': 'Comment added', 'comment': {
            'id': new_comment.id,
            'content': new_comment.content,
            'user_id': new_comment.user_id,
            'created_at': new_comment.created_at.isoformat()
        }}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding comment to Task {task_id}: {str(e)}")
        return jsonify({'error': 'Error adding comment'}), 500

@bp.route('/tasks/<int:task_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(task_id):
    try:
        comments = Comment.query.filter_by(task_id=task_id).all()
        comment_list = [
            {
                'id': comment.id,
                'content': comment.content,
                'user_id': comment.user_id,
                'created_at': comment.created_at.isoformat()
            } for comment in comments
        ]
        return jsonify({'comments': comment_list}), 200
    except Exception as e:
        logging.error(f"Error fetching comments for Task {task_id}: {str(e)}")
        return jsonify({'error': 'Error fetching comments'}), 500


@bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        data = request.get_json()

        comment.content = data.get('content', comment.content)  
        db.session.commit()
        logging.info(f"Comment {comment_id} updated by User {get_jwt_identity()}")
        return jsonify({'message': 'Comment updated'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating comment {comment_id}: {str(e)}")
        return jsonify({'error': 'Error updating comment'}), 500


@bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        logging.info(f"Comment {comment_id} deleted by User {get_jwt_identity()}")
        return jsonify({'message': 'Comment deleted'}), 204

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting comment {comment_id}: {str(e)}")
        return jsonify({'error': 'Error deleting comment'}), 500
@bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': notification.id,
        'message': notification.message,
        'created_at': notification.created_at.isoformat()
    } for notification in notifications]), 200
