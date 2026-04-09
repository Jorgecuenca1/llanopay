import 'package:flutter/material.dart';

import '../config/theme.dart';

/// Bell icon button with a red badge overlay showing unread notification count.
///
/// Includes a subtle scale animation when [animate] is true (new notification).
class NotificationBadge extends StatefulWidget {
  /// Number of unread notifications.
  final int unreadCount;

  /// Callback when the bell icon is pressed.
  final VoidCallback? onTap;

  /// Whether to play the entrance animation (pulse on new notification).
  final bool animate;

  /// Icon color. Defaults to the current icon theme color.
  final Color? iconColor;

  const NotificationBadge({
    super.key,
    required this.unreadCount,
    this.onTap,
    this.animate = false,
    this.iconColor,
  });

  @override
  State<NotificationBadge> createState() => _NotificationBadgeState();
}

class _NotificationBadgeState extends State<NotificationBadge>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    _scaleAnimation = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 1.3), weight: 1),
      TweenSequenceItem(tween: Tween(begin: 1.3, end: 0.9), weight: 1),
      TweenSequenceItem(tween: Tween(begin: 0.9, end: 1.0), weight: 1),
    ]).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    if (widget.animate) {
      _animationController.forward();
    }
  }

  @override
  void didUpdateWidget(NotificationBadge oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.animate && !oldWidget.animate) {
      _animationController.forward(from: 0);
    }
    // Trigger animation when count increases.
    if (widget.unreadCount > oldWidget.unreadCount) {
      _animationController.forward(from: 0);
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: _scaleAnimation,
      child: IconButton(
        onPressed: widget.onTap,
        icon: Stack(
          clipBehavior: Clip.none,
          children: [
            Icon(
              Icons.notifications_outlined,
              size: 28,
              color: widget.iconColor ??
                  Theme.of(context).iconTheme.color,
            ),
            if (widget.unreadCount > 0)
              Positioned(
                right: -4,
                top: -4,
                child: Container(
                  padding: const EdgeInsets.all(2),
                  constraints: const BoxConstraints(
                    minWidth: 18,
                    minHeight: 18,
                  ),
                  decoration: BoxDecoration(
                    color: LlanoPayTheme.error,
                    shape: widget.unreadCount > 9
                        ? BoxShape.rectangle
                        : BoxShape.circle,
                    borderRadius: widget.unreadCount > 9
                        ? BorderRadius.circular(9)
                        : null,
                    border: Border.all(color: Colors.white, width: 1.5),
                  ),
                  child: Center(
                    child: Text(
                      widget.unreadCount > 99
                          ? '99+'
                          : '${widget.unreadCount}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        height: 1,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
