from flask import render_template, make_response, jsonify, request
from sqlalchemy import desc, asc, func, extract, and_, case, text
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from app import app, db, cache
from app.models import User, Product, Server, Updates, History, Workstation, AlchemyEncoder
from app.logger_setup import logger
import json
import datetime
import humanize


def get_date_diff_expression(start_date, end_date):
    """
    Returns a database-agnostic expression for calculating date difference in days.
    Works with SQLite, SQL Server, PostgreSQL, and MySQL.
    """
    # Detect database dialect
    try:
        dialect = db.engine.dialect.name
    except:
        # Fallback if engine not initialized
        dialect = 'sqlite'
    
    if dialect == 'sqlite':
        # SQLite uses julianday
        return func.julianday(end_date) - func.julianday(start_date)
    elif dialect == 'mssql':
        # SQL Server uses DATEDIFF
        return func.datediff(text('day'), start_date, end_date)
    elif dialect == 'postgresql':
        # PostgreSQL uses EXTRACT with epoch
        return func.extract('epoch', end_date - start_date) / 86400.0
    elif dialect == 'mysql':
        # MySQL uses DATEDIFF
        return func.datediff(end_date, start_date)
    else:
        # Fallback: use SQLAlchemy's generic date arithmetic (works for most databases)
        return func.extract('epoch', end_date - start_date) / 86400.0


def get_coalesce_expression(*args):
    """
    Returns a database-agnostic COALESCE expression.
    COALESCE works on SQLite, SQL Server, PostgreSQL, and MySQL.
    """
    return func.coalesce(*args)


def handle_errors(f):
    """Decorator to handle errors in routes with enhanced logging"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except SQLAlchemyError as e:
            # Enhanced database error logging
            error_context = {
                'function': f.__name__,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'args': str(args)[:200],  # Limit length
                'kwargs': {k: str(v)[:100] for k, v in kwargs.items()},
                'request_path': request.path if request else 'N/A',
                'request_method': request.method if request else 'N/A',
            }
            logger.error(f"Database error in {f.__name__}", extra=error_context, exc_info=True)
            db.session.rollback()
            return render_template('error.html', 
                                 message='Database Error', 
                                 detail='An error occurred while accessing the database. Please try again later. If this problem persists, contact your system administrator.'), 500
        except ValueError as e:
            error_context = {
                'function': f.__name__,
                'error_type': 'ValueError',
                'error_message': str(e),
                'request_path': request.path if request else 'N/A',
            }
            logger.warning(f"Value error in {f.__name__}: {str(e)}", extra=error_context)
            return render_template('error.html', 
                                 message='Invalid Request', 
                                 detail=f'The request contained invalid data: {str(e)}. Please check your input and try again.'), 400
        except KeyError as e:
            error_context = {
                'function': f.__name__,
                'error_type': 'KeyError',
                'error_message': str(e),
                'request_path': request.path if request else 'N/A',
            }
            logger.warning(f"Key error in {f.__name__}: {str(e)}", extra=error_context)
            return render_template('error.html', 
                                 message='Missing Required Information', 
                                 detail=f'Required information is missing: {str(e)}. Please ensure all required fields are provided.'), 400
        except Exception as e:
            # Enhanced unexpected error logging
            error_context = {
                'function': f.__name__,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'args': str(args)[:200],
                'kwargs': {k: str(v)[:100] for k, v in kwargs.items()},
                'request_path': request.path if request else 'N/A',
                'request_method': request.method if request else 'N/A',
                'user_agent': request.headers.get('User-Agent', 'N/A') if request else 'N/A',
            }
            logger.error(f"Unexpected error in {f.__name__}", extra=error_context, exc_info=True)
            return render_template('error.html', 
                                 message='An Unexpected Error Occurred', 
                                 detail='An unexpected error occurred while processing your request. Our team has been notified. Please try again later or contact support if the problem persists.'), 500
    return decorated_function


def serialize_dashboard_data(data):
    """serializes current license data for the dashboard"""
    # Original structure: by server, then by product
    obj_by_server = {}
    # New structure: by product, then by server (for tabs)
    obj_by_product = {}
    
    for d in data:
        server_name = d[5]
        product_name = d[2]
        active = d[3]
        total = d[4]
        workstation = d[0]
        username = d[1]
        time_in = d[6]
        
        # Build server-based structure (for backward compatibility)
        if server_name not in obj_by_server:
            obj_by_server[server_name] = {}
        
        if product_name not in obj_by_server[server_name]:
            obj_by_server[server_name][product_name] = {
                'users': [],
                'active': active,
                'total': total
            }
        else:
            # Update active/total if they differ (shouldn't happen, but be safe)
            obj_by_server[server_name][product_name]['active'] = active
            obj_by_server[server_name][product_name]['total'] = total
        
        if time_in is None:
            obj_by_server[server_name][product_name]['users'].append({
                'workstation': workstation,
                'username': username
            })
        
        # Build product-based structure (for tabs)
        if product_name not in obj_by_product:
            obj_by_product[product_name] = {}
        
        if server_name not in obj_by_product[product_name]:
            obj_by_product[product_name][server_name] = {
                'users': [],
                'active': active,
                'total': total
            }
        else:
            # Update active/total if they differ (shouldn't happen, but be safe)
            obj_by_product[product_name][server_name]['active'] = active
            obj_by_product[product_name][server_name]['total'] = total
        
        if time_in is None:
            obj_by_product[product_name][server_name]['users'].append({
                'workstation': workstation,
                'username': username
            })
    
    # Filter out "ArcGIS Pro Advanced" from the products list
    products_list = sorted(obj_by_product.keys())
    # Filter out products with 'advanced' in the name (case-insensitive)
    products_list = [p for p in products_list if 'advanced' not in p.lower()]
    
    return {
        'by_server': obj_by_server,
        'by_product': obj_by_product,
        'products': products_list  # Filtered list of product names for tabs
    }


@app.route('/dashboard')
@app.route('/')
@cache.cached(timeout=60, key_prefix='dashboard')  # Cache for 60 seconds
@handle_errors
def dashboard():
    server_count = db.session.query(Server).count()
    user_count = db.session.query(User).count()
    product_count = db.session.query(Product).count()
    workstation_count = db.session.query(Workstation).count()
    active_user_count = db.session.query(User).join(History).filter(History.time_in == None).join(
        Product).filter( Product.type == 'core').count()

    active = db.session.query(Workstation.name, User.name, Product.common_name, Product.license_out,
                              Product.license_total, Server.name, History.time_in). \
        filter(History.user_id == User.id,
               History.update_id == Updates.id,
               History.workstation_id == Workstation.id,
               Product.server_id == Server.id,
               History.product_id == Product.id).all()

    detail = serialize_dashboard_data(active)
    return render_template('index.html',
                           server_count=server_count,
                           user_count=user_count,
                           active_user_count=active_user_count,
                           product_count=product_count,
                           workstation_count=workstation_count,
                           detail=detail)

@app.route('/data/server/availability')
@handle_errors
def server_availability():
    """
    Gets the core and extension product availability on a license server.
    :return: Availability of products on a license server.
    """
    s = request.args.get('servername')
    if not s:
        return jsonify({'error': 'servername parameter is required'}), 400
    
    # Sanitize input - only allow alphanumeric, dash, underscore, and dot
    if not all(c.isalnum() or c in '-_.' for c in s):
        return jsonify({'error': 'Invalid servername format'}), 400
    
    try:
        core = db.session.query(Product, Server).filter(Product.type == 'core'). \
            filter(Product.server_id == Server.id).filter(Server.name == s).all()
        ext = db.session.query(Product, Server).filter(Product.type == 'extension'). \
            filter(Product.server_id == Server.id).filter(Server.name == s).all()
        return json.dumps(core + ext, cls=AlchemyEncoder)
    except Exception as e:
        logger.error(f"Error in server_availability: {str(e)}")
        return jsonify({'error': 'Failed to retrieve server availability'}), 500


@app.route('/data/product/availability')
@handle_errors
def product_availability():
    """
    :return: Active users by product name
    """
    sname = request.args.get('servername')
    pname = request.args.get('product')
    
    if not sname or not pname:
        return jsonify({'error': 'servername and product parameters are required'}), 400
    
    # Sanitize inputs
    if not all(c.isalnum() or c in '-_. /' for c in sname):
        return jsonify({'error': 'Invalid servername format'}), 400
    if not all(c.isalnum() or c in '-_. /' for c in pname):
        return jsonify({'error': 'Invalid product name format'}), 400
    
    try:
        active = db.session.query(User.name, Workstation.name, Product.common_name,
                                  History.time_in, History.time_out, Server.name). \
            filter(User.id == History.user_id). \
            filter(Product.id == History.product_id). \
            filter(Workstation.id == History.workstation_id). \
            filter(Server.id == Product.server_id). \
            filter(Product.internal_name == pname). \
            filter(Server.name == sname). \
            filter(History.time_in == None).all()
        return jsonify(results=[[x for x in a] for a in active])
    except Exception as e:
        logger.error(f"Error in product_availability: {str(e)}")
        return jsonify({'error': 'Failed to retrieve product availability'}), 500


@app.route('/data/active_users')
@handle_errors
def active_users():
    try:
        active = db.session.query(User).join(History).filter(History.time_in == None).join(
            Product).filter(
            Product.type == 'core').all()
        # Return JSON instead of raw objects
        return jsonify([{'id': u.id, 'name': u.name} for u in active])
    except Exception as e:
        logger.error(f"Error in active_users: {str(e)}")
        return jsonify({'error': 'Failed to retrieve active users'}), 500


@app.route('/products')
@handle_errors
def products():
    all_products = db.session.query(Product.common_name, Product.license_out, Product.license_total, Server.name).filter(Product.server_id==Server.id).all()
    return render_template('pages/products.html',
                           products=all_products)


@app.route('/products/<product_name>')
@handle_errors
def productname(product_name):
    # Sanitize product name from URL
    if not product_name or len(product_name) > 100:
        return render_template('error.html', 
                             message='Invalid Product Name', 
                             detail='The product name provided is invalid.'), 400
    # Use database-agnostic date calculation
    time_in_expr = get_coalesce_expression(History.time_in, datetime.datetime.now())
    time_diff = get_date_diff_expression(History.time_out, time_in_expr)
    
    users = db.session.query(User.name, History.time_in,
                             Server.name.label('servername'),
                             func.sum(time_diff).label('time_sum')). \
        filter(User.id == History.user_id). \
        filter(History.product_id == Product.id). \
        filter(Product.server_id == Server.id). \
        filter(Product.common_name == product_name). \
        distinct(User.name).group_by(User.name).all()

    # days = datetime.datetime.utcnow() - datetime.timedelta(days=days)

    # chart_data = db.session.query(func.count(History.user_id).label('users'), Product.license_total,
    #                               extract('month', History.time_out).label('m'),
    #                               extract('day', History.time_out).label('d'),
    #                               extract('year', History.time_out).label('y')). \
    #     filter(Product.id == History.product_id). \
    #     filter(Server.id == Updates.server_id). \
    #     filter(Updates.id == History.update_id). \
    #     filter(Server.name == server_name). \
    #     filter(Product.common_name == product_name). \
    #     distinct(History.user_id). \
    #     group_by(Product.common_name, Server.name, 'm', 'd', 'y'). \
    #     order_by(desc('y')).order_by(desc('m')).order_by(desc('d')).all()
    #  filter(History.time_out > days).

    # info = db.session.query(Product). \
    #     filter(Server.id == Product.server_id). \
    #     filter(Server.name == server_name). \
    #     filter(Product.common_name == product_name).first()
    return render_template('pages/productname.html',
                           users=users,
                           # chart_data=chart_data,
                           # info=info
                           )


# @app.route('/_productchart')
# def productchart():
#     selection = request.args.get('days')
#     servername = request.args.get('servername')
#     productname = request.args.get('productname')
#     days = datetime.datetime.utcnow() - datetime.timedelta(days=int(selection))
#     chart_data = db.session.query(func.count(History.user_id).label('users'), Product.license_total,
#                                   extract('month', History.time_out).label('m'),
#                                   extract('day', History.time_out).label('d'),
#                                   extract('year', History.time_out).label('y')). \
#         filter(Product.id == History.product_id). \
#         filter(Server.id == Updates.server_id). \
#         filter(Updates.id == History.update_id). \
#         filter(Server.name == servername). \
#         filter(History.time_out > days). \
#         filter(Product.common_name == productname). \
#         distinct(History.user_id). \
#         group_by(Product.common_name, Server.name, 'm', 'd', 'y'). \
#         order_by(desc('y')).order_by(desc('m')).order_by(desc('d')).all()
#     return jsonify(result=chart_data)


@app.route('/users')
@handle_errors
def users():
    # Use database-agnostic date calculation
    time_in_expr = get_coalesce_expression(History.time_in, datetime.datetime.now())
    time_diff = get_date_diff_expression(History.time_out, time_in_expr)
    
    all_users = db.session.query(User.name, History.time_in,
                                 func.sum(time_diff).label('time_sum')). \
        filter(User.id == History.user_id). \
        filter(History.product_id == Product.id). \
        filter(Product.type == 'core'). \
        distinct(User.name).group_by(User.name).all()
    return render_template('pages/users.html',
                           users=all_users)


@app.route('/users/<username>')
@handle_errors
def username(username):
    # Sanitize username from URL
    if not username or len(username) > 100:
        return render_template('error.html', 
                             message='Invalid Username', 
                             detail='The username provided is invalid.'), 400
    workstations = db.session.query(Workstation, History). \
        filter(User.id == History.user_id). \
        filter(Workstation.id == History.workstation_id). \
        group_by(Workstation.name).distinct(Workstation.name). \
        filter(User.name == username).all()

    servers = db.session.query(Server, History). \
        filter(User.id == History.user_id). \
        filter(Updates.id == History.update_id). \
        filter(Server.id == Updates.server_id). \
        filter(User.name == username). \
        group_by(Server.name).distinct(Server.name).all()

    # Use database-agnostic date calculation
    time_in_expr = get_coalesce_expression(History.time_in, datetime.datetime.now())
    time_diff = get_date_diff_expression(History.time_out, time_in_expr)
    
    products = db.session.query(Product.common_name, Product.type, History.time_in,
                                func.sum(time_diff).label('time_sum')). \
        filter(User.id == History.user_id). \
        filter(User.name == username). \
        filter(History.product_id == Product.id). \
        group_by(Product.common_name).distinct(Product.common_name).all()
    return render_template('pages/username.html',
                           workstations=workstations,
                           servers=servers,
                           products=products)


@app.route('/servers')
@handle_errors
def servers():
    query = db.session.query(
        Server.name.label("name"),
        Updates.info.label("info"),
        Updates.status.label("status"),
        Server.id == Updates.server_id,
        func.max(Updates.time_complete).label('maxdate')
    ).filter(Server.id == Updates.server_id).group_by(Server.name).all()
    return render_template('pages/servers.html', servers=query)


@app.route('/servers/<servername>')
@handle_errors
def servername(servername):
    # Sanitize servername from URL
    if not servername or len(servername) > 100:
        return render_template('error.html', 
                             message='Invalid Server Name', 
                             detail='The server name provided is invalid.'), 400
    status = db.session.query(Server, Updates). \
        filter(Server.id == Updates.server_id). \
        filter(Server.name == servername). \
        order_by(desc(Updates.time_start)).limit(1).first()
    history = db.session.query(Server, Updates). \
        filter(Server.id == Updates.server_id). \
        filter(Server.name == servername). \
        filter(Updates.status != 'UP'). \
        order_by(desc(Updates.time_start)).all()
    users = db.session.query(User, History, Server, Updates, Product). \
        filter(User.id == History.user_id). \
        filter(Updates.id == History.update_id). \
        filter(Product.id == History.product_id). \
        filter(Server.id == Updates.server_id). \
        filter(Product.type == 'core'). \
        filter(Server.name == servername). \
        distinct(User.name).group_by(User.name).all()
    first_update = db.session.query(Updates). \
        filter(Server.id == Updates.server_id). \
        filter(Server.name == servername). \
        order_by(asc(Updates.time_start)).limit(1).first()
    return render_template('pages/servername.html',
                           chart_data=None,
                           status=status,
                           history=history,
                           users=users,
                           start_date=first_update)

#TODO: clear log for updates on server
def clear_log(servername):
    try:
        Updates.clear()
        return make_response('ok', 200)
    except Exception as e:
        return make_response(str(e), 500)


@app.route('/workstations')
@handle_errors
def workstations():
    # Use database-agnostic date calculation
    time_in_expr = get_coalesce_expression(History.time_in, datetime.datetime.now())
    time_diff = get_date_diff_expression(History.time_out, time_in_expr)
    
    all_ws = db.session.query(Workstation.name, History.time_in,
                              func.sum(time_diff).label('time_sum')). \
        filter(Workstation.id == History.workstation_id). \
        filter(History.product_id == Product.id). \
        filter(Product.type == 'core'). \
        distinct(Workstation.name).group_by(Workstation.name).all()
    return render_template('pages/workstations.html',
                           ws=all_ws)


@app.route('/workstations/<workstationname>')
@handle_errors
def workstationname(workstationname):
    # Sanitize workstation name from URL
    if not workstationname or len(workstationname) > 100:
        return render_template('error.html', 
                             message='Invalid Workstation Name', 
                             detail='The workstation name provided is invalid.'), 400
    users = db.session.query(User.name, History.time_in). \
        filter(User.id == History.user_id). \
        filter(Workstation.id == History.workstation_id). \
        group_by(User.name).distinct(User.name). \
        filter(Workstation.name == workstationname).all()

    servers = db.session.query(Server, History.time_in). \
        filter(Workstation.id == History.workstation_id). \
        filter(Updates.id == History.update_id). \
        filter(Server.id == Updates.server_id). \
        filter(Workstation.name == workstationname). \
        group_by(Server.name).distinct(Server.name).all()

    # Use database-agnostic date calculation
    time_in_expr = get_coalesce_expression(History.time_in, datetime.datetime.now())
    time_diff = get_date_diff_expression(History.time_out, time_in_expr)
    
    products = db.session.query(Product.common_name, Product.type, History.time_in,
                                func.sum(time_diff).label('time_sum')). \
        filter(Workstation.id == History.workstation_id). \
        filter(Workstation.name == workstationname). \
        filter(History.product_id == Product.id). \
        group_by(Product.common_name).distinct(Product.common_name).all()
    return render_template('pages/workstationname.html',
                           users=users,
                           servers=servers,
                           products=products)


@app.context_processor
def utility_processor():
    def pluralize(i, s):
        if i != 1:
            return s + 's'
        else:
            return s

    return dict(pluralize=pluralize)


@app.template_filter('relative_time')
def relative_time(t):
    if t:
        try:
            humanized = humanize.naturaltime(t)
            return humanized
        except ValueError as v:
            print(v)
            return '0s'
    else:
        return None


@app.template_filter('delta_time')
def delta_time(t):
    if t:
        try:
            h = humanize.naturaldelta(datetime.timedelta(days=t))
            return h
        except ValueError as v:
            print(v)
            return '0'
    else:
        return None
