import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';

import '../../blocs/wallet/wallet_bloc.dart';
import '../../blocs/wallet/wallet_event.dart';
import '../../blocs/wallet/wallet_state.dart';
import '../../config/theme.dart';

class TransactionDetailScreen extends StatefulWidget {
  final String transactionId;

  const TransactionDetailScreen({
    super.key,
    required this.transactionId,
  });

  @override
  State<TransactionDetailScreen> createState() =>
      _TransactionDetailScreenState();
}

class _TransactionDetailScreenState extends State<TransactionDetailScreen> {
  final _copFormat = NumberFormat.currency(
    locale: 'es_CO',
    symbol: '\$',
    decimalDigits: 0,
  );

  @override
  void initState() {
    super.initState();
    context
        .read<WalletBloc>()
        .add(TransactionDetailRequested(id: widget.transactionId));
  }

  Color _statusColor(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'completada':
        return LlanoPayTheme.success;
      case 'pending':
      case 'pendiente':
        return LlanoPayTheme.secondaryGold;
      case 'failed':
      case 'fallida':
        return LlanoPayTheme.error;
      case 'cancelled':
      case 'cancelada':
        return LlanoPayTheme.textSecondary;
      default:
        return LlanoPayTheme.primaryGreen;
    }
  }

  String _statusLabel(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'Completada';
      case 'pending':
        return 'Pendiente';
      case 'failed':
        return 'Fallida';
      case 'cancelled':
        return 'Cancelada';
      default:
        return status;
    }
  }

  IconData _typeIcon(String type) {
    switch (type) {
      case 'deposit':
        return Icons.arrow_downward;
      case 'withdrawal':
        return Icons.arrow_upward;
      case 'transfer':
        return Icons.swap_horiz;
      case 'crypto_deposit':
        return Icons.currency_bitcoin;
      case 'purchase':
        return Icons.store;
      case 'microcredit':
        return Icons.credit_score;
      default:
        return Icons.receipt_long;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Detalle de Transaccion'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: BlocBuilder<WalletBloc, WalletState>(
        builder: (context, state) {
          if (state is WalletLoading) {
            return const Center(
              child: CircularProgressIndicator(
                color: LlanoPayTheme.primaryGreen,
              ),
            );
          }

          if (state is WalletError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 48, color: LlanoPayTheme.error),
                  const SizedBox(height: 12),
                  Text(state.message),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () {
                      context.read<WalletBloc>().add(
                            TransactionDetailRequested(
                              id: widget.transactionId,
                            ),
                          );
                    },
                    child: const Text('Reintentar'),
                  ),
                ],
              ),
            );
          }

          if (state is TransactionDetailLoaded) {
            return _buildDetail(state.transaction);
          }

          return const SizedBox.shrink();
        },
      ),
    );
  }

  Widget _buildDetail(Map<String, dynamic> tx) {
    final type = tx['type'] as String? ?? 'transfer';
    final amount = (tx['amount'] as num?)?.toDouble() ?? 0;
    final status = tx['status'] as String? ?? 'pending';
    final reference = tx['reference'] as String? ?? '-';
    final description = tx['description'] as String? ?? '';
    final date = tx['created_at'] as String? ?? '';
    final balanceAfter = (tx['balance_after'] as num?)?.toDouble();
    final isIncome = amount >= 0;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SizedBox(height: 16),

          // -- Type icon --
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              color: (isIncome ? LlanoPayTheme.success : LlanoPayTheme.error)
                  .withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              _typeIcon(type),
              size: 36,
              color: isIncome ? LlanoPayTheme.success : LlanoPayTheme.error,
            ),
          ),

          const SizedBox(height: 20),

          // -- Amount --
          Text(
            '${isIncome ? '+' : ''}${_copFormat.format(amount)} COP',
            style: GoogleFonts.montserrat(
              fontSize: 32,
              fontWeight: FontWeight.w800,
              color: isIncome ? LlanoPayTheme.success : LlanoPayTheme.error,
            ),
          ),

          const SizedBox(height: 12),

          // -- Status badge --
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            decoration: BoxDecoration(
              color: _statusColor(status).withOpacity(0.12),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              _statusLabel(status),
              style: GoogleFonts.montserrat(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: _statusColor(status),
              ),
            ),
          ),

          const SizedBox(height: 32),

          // -- Detail rows --
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _detailRow('Referencia', reference),
                  const Divider(height: 24),
                  _detailRow(
                    'Fecha',
                    date.isNotEmpty
                        ? DateFormat('dd MMMM yyyy, hh:mm a', 'es_CO')
                            .format(DateTime.tryParse(date) ?? DateTime.now())
                        : '-',
                  ),
                  const Divider(height: 24),
                  _detailRow('Tipo', type),
                  if (description.isNotEmpty) ...[
                    const Divider(height: 24),
                    _detailRow('Descripcion', description),
                  ],
                  if (balanceAfter != null) ...[
                    const Divider(height: 24),
                    _detailRow(
                      'Saldo despues',
                      '${_copFormat.format(balanceAfter)} COP',
                    ),
                  ],
                ],
              ),
            ),
          ),

          const SizedBox(height: 32),

          // -- Share receipt button --
          SizedBox(
            width: double.infinity,
            height: 52,
            child: OutlinedButton.icon(
              onPressed: () {
                final receiptText = StringBuffer()
                  ..writeln('--- Recibo LlanoPay ---')
                  ..writeln('Referencia: $reference')
                  ..writeln(
                      'Monto: ${isIncome ? '+' : ''}${_copFormat.format(amount)} COP')
                  ..writeln('Estado: ${_statusLabel(status)}')
                  ..writeln(
                    'Fecha: ${date.isNotEmpty ? DateFormat('dd/MM/yyyy hh:mm a', 'es_CO').format(DateTime.tryParse(date) ?? DateTime.now()) : '-'}',
                  )
                  ..writeln('Descripcion: $description')
                  ..writeln('-----------------------');

                Clipboard.setData(ClipboardData(text: receiptText.toString()));
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Recibo copiado al portapapeles'),
                    backgroundColor: LlanoPayTheme.success,
                  ),
                );
              },
              icon: const Icon(Icons.share_outlined),
              label: const Text('Compartir recibo'),
            ),
          ),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _detailRow(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 2,
          child: Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: LlanoPayTheme.textSecondary,
                ),
          ),
        ),
        Expanded(
          flex: 3,
          child: Text(
            value,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
            textAlign: TextAlign.end,
          ),
        ),
      ],
    );
  }
}
