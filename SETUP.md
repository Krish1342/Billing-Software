# Jewelry Management System - Supabase Setup Guide

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Supabase Setup

1. Go to [Supabase](https://supabase.com) and create a new project
2. Wait for the project to be ready (usually 2-3 minutes)
3. Go to Settings → API to get your credentials
4. Note down:
   - Project URL (looks like: `https://your-project-id.supabase.co`)
   - Anon public key (starts with `eyJ...`)

### 3. Database Setup

1. In Supabase dashboard, go to SQL Editor
2. Copy and paste the entire content of `database/supabase_schema.sql`
3. Click "Run" to create all tables, functions, and views
4. Verify success by checking the Tables tab - you should see categories, inventory, suppliers, etc.

### 4. Environment Configuration

1. Copy `.env.template` to `.env`
2. Fill in your Supabase credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

### 5. Run the Application

```bash
python main.py
```

## ✅ Verification

### Test Database Connection

Run the PyQt example to test your setup:

```bash
python examples/pyqt_supabase_example.py
```

### Run Test Cases

In Supabase SQL Editor, run:

```sql
-- Copy and paste from database/test_cases.sql
```

## 🔄 Migration from Existing System

If you have existing data, follow the migration guide in `database/migration_guide.md`.

## 📊 Key Features Enabled

✅ **Serialized Inventory**: Each jewelry piece is individually tracked  
✅ **Category Item Numbers**: Reusable sequential IDs per category  
✅ **Atomic Stock Operations**: Safe concurrent bill creation  
✅ **Bill Reversal**: Restore sold items back to inventory  
✅ **CSV Export**: Category and summary data export  
✅ **Real-time Updates**: Live inventory tracking  
✅ **Audit Trail**: Complete stock movement history

## 🛠️ Troubleshooting

**Connection Issues:**

- Verify SUPABASE_URL and SUPABASE_ANON_KEY in .env
- Check internet connection
- Ensure Supabase project is active

**Database Errors:**

- Run test_cases.sql to validate schema
- Check Supabase logs in dashboard
- Verify all RPC functions were created

**Application Issues:**

- Check Python version (3.8+ required)
- Verify all dependencies installed
- Check console output for errors

## 📈 Next Steps

1. **Add Initial Data**: Use the Stock Management tab to add categories, suppliers, and inventory
2. **Create First Bill**: Use the Billing tab to test the complete workflow
3. **Export Data**: Test CSV export functionality
4. **Monitor Performance**: Check Supabase dashboard for usage metrics

## 🔒 Security Notes

- Keep your `.env` file private (never commit to version control)
- Use environment variables in production
- Consider Row Level Security (RLS) policies for multi-user setups
- Regular backups recommended via Supabase dashboard

## 📞 Support

- Review `database/operational_notes.md` for advanced configuration
- Check PyQt examples in `examples/` directory
- Supabase documentation: https://supabase.com/docs
